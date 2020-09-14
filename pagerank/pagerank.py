import os
import random
import re
import sys
import numpy as np

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    pages = list(corpus)
    links = corpus.get(page)
    page_prob_dist = dict()

    # If no links, choose randomly, else, (1-d) to choose any page, and
    # (d) to choose any linked page
    if len(links) == 0:
        base_probability = 1 / len(pages)
        for page in pages:
            page_prob_dist[page] = base_probability
    # else, (1-d) to choose any page, and (d) to choose any linked page
    else:
        base_probability = (1-damping_factor) / len(pages)
        redirection_prob = damping_factor / len(links)
        for page in pages:
            if page in links:
                page_prob_dist[page] = base_probability + redirection_prob
            else:
                page_prob_dist[page] = base_probability

    return page_prob_dist
    
    # numpy version
    # if len(links) == 0:
    #     page_prob_dist = np.full((len(pages)), 1 / len(pages))
    # else:
    #    pages = np.asarray(pages)
    #    links = np.asarray(list(links))
    #     mask = np.isin(pages, links)
    #     page_prob_dist = np.full((len(pages)), base_probability)
    #     page_prob_dist[mask] += redirection_prob
    # page_prob_dist = dict(zip(pages, page_prob_dist))

    # comparison
    # page1 = list(page_prob_dist.values())
    # page2 = list(page_prob_dist.values())
    # comparison_list = [abs(page1[i] - page2[i]) for i in range(len(page1))]
    # if max(comparison_list) > 0:
    #     print("DIFF.")


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages = list(corpus)
    pagerank_total = {page:0 for page in pages}

    # initialise loop
    current_page = pages[random.randint(0, len(pages) - 1)]
    if current_page in pages:
        pagerank_total[current_page] += 1
    else:
        raise "Unrecognized Page"

    #initialise set of transition models for small sample sets
    if len(pages) < 5000:
        model_set = dict()
        for page in pages:
            model_set[page] = transition_model(corpus, page, damping_factor)

    # start of n loops, n-1 due to initialisation.
    rng = np.random.default_rng()
    for i in range(n - 1):
        if len(pages) < 5000:
            sample_model = model_set.get(current_page)
        else:
            sample_model = transition_model(corpus, current_page, damping_factor)
        page_prob_dist = [sample_model[page] for page in pages]
        current_page = rng.choice(pages, p=page_prob_dist) # random based on give probability
        if current_page in pages:
            pagerank_total[current_page] += 1
        else:
            raise "Unrecognized Page" # sanity check lest wrong page

    # makes sum of views into probability format
    pagerank_prob = {key: value / n for key, value in pagerank_total.items()}

    if round(sum(pagerank_prob.values()), 5) == 1:
        return pagerank_prob
    else:
        raise ValueError

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages = list(corpus)
    # pages with no links == link to all pages
    for key, value in corpus.items():
        if len(value) == 0:
            corpus[key] = set(pages)
    links = list(corpus.values())

    # produces a list of incoming links for each page in corpus
    incoming_links = []
    for page in pages:
        inner = []
        for key, value in corpus.items():
            if page in value:
                inner.append(key)
        incoming_links.append(inner)
    incoming_links = [[pages.index(j) for j in incoming_links[i]] for i in range(len(incoming_links))]

    # initialise values for pagerank
    numlink = [len(i) for i in links]
    pagerank = [(1 / len(pages)) for i in range(len(pages))] # initialise
    random_page_const = (1-DAMPING) / len(pages)

    # Iterate till pagerank convergence
    while True:
        pagerank_next = [random_page_const + (DAMPING * sum([pagerank[j] / numlink[j] for j in i])) for i in incoming_links]
        change = max([abs(pagerank[i] - pagerank_next[i]) for i in range(len(pagerank))])
        if change < 0.001:
            break
        pagerank = pagerank_next

    pagerank_results = dict()
    for i in range(len(pages)):
        pagerank_results[pages[i]] = pagerank[i]
    return pagerank_results


if __name__ == "__main__":
    main()

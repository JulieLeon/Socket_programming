import argparse
import itertools
import logging
from mpi4py import MPI
import sys
import time

# Create a logger for this module
logger = logging.getLogger(__name__)

def read_args():
    """Read command line arguments."""

    # Define parser
    parser = argparse.ArgumentParser(
        description='A parallelized sort using sockets.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i', '--input', help=('Path to input file.'))
    parser.add_argument('-o', '--output', help='Path to output file.')
    parser.add_argument('-v', '--verbose', action='count', default=0,
            help='Set verbose level.')

    # Parse arguments
    args = parser.parse_args()

    # Enable debug messages
    if args.verbose >= 1:
        logger.setLevel(logging.INFO)
    if args.verbose >= 2:
        logger.setLevel(logging.DEBUG)

    # Check arguments
    if args.input is None or args.output is None:
        raise ValueError(("An input file and an output file are required."))

    return args

def load_words(file):
    
    # Read all lines
    with open(file, 'r') as f:
        words = f.readlines()

    # Remove end-of-line characters
    words = [w.strip() for w in words]
    
    return words

def save_words(words, file):
    
    with open(file, 'w') as f:
        f.write('\n'.join(words))
        if len(words) > 0:
            f.write('\n')

def divide_words(words, n):

    # Divide list of words between server and clients
    # Last range will be for the server
    nb_words_per_process = len(words) // n
    indices = [i * nb_words_per_process for i in range(n)]
    indices.append(len(words))
    return indices

def merge_sorted_sublists_inplace(x, begin, middle, end):
    # Merge two adjacent sub-lists inside the same array
    #
    # x:      The source list to sort, in-place.
    # begin:  Start index, included.
    # middle: Start of second list, included.
    # end:    End index, excluded.

    # We iterate on both sub-lists at the same time, selecting each time the
    # lowest element.
    # We thus need two indices.
    i = begin  # Index on first sub-list.
    j = middle # Index on second sub-list.
    while i < middle and j < end:
    
        # ith element (first sub-list) is at right place
        if x[i] <= x[j]:
            i += 1
            
        # jth element (second sub-list) must be moved at ith position
        else:
            
            # Store value of jth element
            w = x[j]
            
            # Switch elements from position to position j - 1 to the right
            for k in range(j, i, -1):
                x[k] = x[k - 1]
                
            # Copy value of jth element at position i
            x[i] = w
            
            # Increment counters
            i += 1
            j += 1
            
            # The middle element has moved to the right
            middle += 1

def merge_sorted_sublists(b, begin, middle, end, a):
    # Merge two adjacent sub-lists inside the same array
    #
    # begin:  Start index, included.
    # middle: Start of second list, included.
    # end:    End index, excluded.
    # a:      The source list to sort.
    # b:      The destination list where to copy sorted items.

    # We iterate on both sub-lists at the same time, selecting each time the
    # lowest element.
    # We thus need two indices.
    i = begin  # Index on first sub-list.
    j = middle # Index on second sub-list.
    
    # Process all elements of both sub-lists
    for k in range(begin, end):
        
        # We choose current element (index i) of first sub-list
        if i < middle and (j >= end or a[i] <= a[j]):
            b[k] = a[i]
            i += 1

        # We choose current element (index j) of second sub-list
        else:
            b[k] = a[j]
            j += 1

def merge_sort(b, begin, end, a):
    # begin: Start index, included.
    # end:   End index, excluded.
    # a:     The source list to sort.
    # b:     The destination list where to copy sorted items.
    
    # One element
    if end - begin <= 1:
        return

    # Get middle index
    middle = (begin + end) // 2
    
    # Sort the two sub-lists from b into a
    merge_sort(a, begin, middle, b)
    merge_sort(a, middle, end, b)
    
    # Merge sorted sub-lists from a into b
    merge_sorted_sublists(b, begin, middle, end, a)

if __name__ == "__main__":

    # Setup the logger
    handler = logging.StreamHandler(sys.stderr)
    logger.addHandler(handler)

    # Read command line arguments
    args = read_args()

    # Get communication channel
    comm = MPI.COMM_WORLD

    # Get my rank among processes
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Prepare data to pass
    if rank == 0:

        # Load input words
        words = load_words(args.input)

        # Record start time
        start_time = time.perf_counter()

        # Split words
        indices = divide_words(words, size)
        logger.debug("Indices: %s" % indices)
        data = [words[indices[i]:indices[i+1]] for i in range(size)]

    # Sub-processes
    else:
        data = None
    logger.debug("Scattered data of %d: %s" % (rank, data))

    # Scatter data among processes
    my_words = comm.scatter(data, root=0)
    logger.debug("Words of %d: %s" % (rank, my_words))

    # Sort
    my_words_2 = my_words.copy()
    logger.debug("my_words_2 of %d: %s" % (rank, my_words_2))
    merge_sort(my_words, 0, len(my_words), my_words_2)
    logger.debug("Sorted words of %d: %s" % (rank, my_words))

    # Gather data
    data = comm.gather(my_words, root=0)
    logger.debug("Gathered DATA (rank %d): %s" % (rank, data))

    # Put back the lists together and run the final merge sort
    if rank == 0:

        # Join
        words = list(itertools.chain(*data))

        # Merge
        for i in range(1, size):
            merge_sorted_sublists_inplace(words, 0, indices[i], indices[i+1])
        logger.debug("Sorted words: %s" % words)
    
        # Print elapsed time
        sys.stderr.write("Elasped time: %f s\n" % (time.perf_counter() -
            start_time))

        # Write sorted words to output file
        save_words(words, args.output)

    # Quit program properly
    quit(0)

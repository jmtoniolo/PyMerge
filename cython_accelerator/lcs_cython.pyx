#cython: boundscheck=False
#standard cimport file libc/stdlib.pxd
#cython: language_level=3
#cythonL optimize.use_switch=True
#cython: infer_types=True
#cython: initializedcheck=False
#cython: optimize.unpack_method_calls=True
#cython: cdivision=True
#cython: Cython.Compiler.Options.gcc_branch_hints=True
#cython: Cython.Compiler.Options.lookup_module_cpdef=False
#cython: Cython.Compiler.Options.cache_builtins=True
#cython: Cython.Compiler.Options.clear_to_none=False
#cython: Cython.wraparound=False

cdef longest_common_subsequence(left_set, right_set):
    cdef unsigned int left_set_size = len(left_set)
    cdef unsigned int right_set_size = len(right_set)
    cdef unsigned int total_size = left_set_size + right_set_size
    cdef unsigned int array_size = 2 * total_size + 1
    bounded_array = [0] * array_size
    k_candidates = [None] * array_size
    outp = [[], []]
    cdef int  x_idx = 0
    cdef int  y_idx = 0
    cdef int  idx = 0

    for d in range(total_size + 1):
        for k in range(-d, d + 1, 2):
            if k == -d or (
                k != d and bounded_array[total_size + k - 1] < bounded_array[total_size + k + 1]
            ):
                idx = total_size + k + 1
                x_idx = bounded_array[idx]
            else:
                idx = total_size + k - 1
                x_idx = bounded_array[idx] + 1
            y_idx = x_idx - k
            snake = k_candidates[idx]
            while x_idx < left_set_size and y_idx < right_set_size and left_set[x_idx] == right_set[y_idx]:
                snake = ((x_idx, y_idx), snake)
                x_idx += 1
                y_idx += 1
            if x_idx >= left_set_size and y_idx >= right_set_size:
                while snake:
                    outp[0].append(snake[0][0])
                    outp[1].append(snake[0][1])
                    snake = snake[1]
                outp[0].reverse()
                outp[1].reverse()
                return outp
            bounded_array[total_size + k] = x_idx
            k_candidates[total_size + k] = snake




# Pass your match list to this
cdef pad_raw_line_matches(match_list, int file_length_max):
    cdef unsigned int m = len(match_list[0])
    cdef unsigned int n = len(match_list[1])
    cdef int idx = 0
    cdef int cntr = 0
    outp_list = [[], []]
    cdef unsigned int r_ = 0
    cdef unsigned int n_ = 0

    while r_ < (
            max(match_list[0][idx] - 0, match_list[1][idx] - 0) - 1):
        outp_list[0].append(-1)
        outp_list[1].append(-1)
        r_ += 1
    r_ = 0

    while n_ < max(m, n):
        while r_ < (
                max(match_list[0][idx] - match_list[0][idx - 1], match_list[1][idx] - match_list[1][idx - 1]) - 1):
            outp_list[0].append(-1)
            outp_list[1].append(-1)
            cntr += 1
            r_ += 1
        outp_list[0].append(match_list[0][idx])
        outp_list[1].append(match_list[1][idx])
        idx += 1
        cntr += 1
        n_ += 1

    return outp_list


def padded_lcs(right_set, left_set, myers=True):
    if myers:
        raw_matches = longest_common_subsequence(right_set, left_set)
    return pad_raw_line_matches(raw_matches, 0)

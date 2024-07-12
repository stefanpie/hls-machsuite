# Kernel Descriptions

## aes_aes

An implementation of AES-256 encryption in Electronic Codebook (ECB) mode. The kernel performs the encryption operation on a 16-byte block of data using a 256-bit key. The design is byte-oriented, meaning it operates on individual bytes of the data and key, and all lookup tables have been replaced with on-the-fly calculations.

Top-Level Function: `aes256_encrypt_ecb`

Inputs:

- `ctx`: a pointer to an `aes256_context` structure, which contains the encryption key and other necessary information
- `k`: a 32-byte array containing the 256-bit encryption key
- `buf`: a 16-byte array containing the plaintext data to be encrypted

Outputs:

- `buf`: the encrypted 16-byte array

Important Data Structures and Data Types:

- `aes256_context`: a structure containing the encryption key, encryption key schedule, and decryption key schedule
- `uint8_t`: an unsigned 8-bit integer type used to represent individual bytes of data and key

Sub-Components:

- `aes_subBytes`: a function that substitutes each byte of the data with a corresponding byte from the S-box
- `aes_addRoundKey`: a function that adds the round key to the data
- `aes_shiftRows`: a function that shifts the rows of the data matrix
- `aes_mixColumns`: a function that mixes the columns of the data matrix
- `aes_expandEncKey`: a function that expands the encryption key schedule
- `rj_sbox`: a function that calculates the S-box value for a given byte
- `rj_xtime`: a function that calculates the xtime value for a given byte
- `gf_alog` and `gf_log`: functions that calculate the anti-logarithm and logarithm, respectively, in the Galois field
- `gf_mulinv`: a function that calculates the multiplicative inverse in the Galois field

## bfs_bulk

An implementation of the Breadth-First Search (BFS) algorithm for graph traversal. The algorithm starts from a given starting node and explores the graph level by level, marking each node with its distance from the starting node. The design is optimized for large graphs and uses a bulk-synchronous parallel approach to achieve high performance.

Top-Level Function: `bfs`

Inputs:

- `nodes`: an array of `node_t` structures, each representing a node in the graph, with `edge_begin` and `edge_end` fields indicating the range of edges connected to the node.
- `edges`: an array of `edge_t` structures, each representing an edge in the graph, with a `dst` field indicating the destination node of the edge.
- `starting_node`: a `node_index_t` value indicating the starting node of the BFS traversal.
- `level`: an array of `level_t` values, where each element represents the level (distance from the starting node) of the corresponding node in the graph.
- `level_counts`: an array of `edge_index_t` values, where each element represents the number of nodes at the corresponding level.

Outputs:

- `level`: the updated array of `level_t` values, where each element represents the level (distance from the starting node) of the corresponding node in the graph.
- `level_counts`: the updated array of `edge_index_t` values, where each element represents the number of nodes at the corresponding level.

Important Data Structures and Data Types:

- `node_t`: a struct representing a node in the graph, with `edge_begin` and `edge_end` fields indicating the range of edges connected to the node.
- `edge_t`: a struct representing an edge in the graph, with a `dst` field indicating the destination node of the edge.
- `level_t`: an 8-bit signed integer type used to represent the level (distance from the starting node) of each node in the graph.
- `edge_index_t`: a 64-bit unsigned integer type used to represent edge indices.
- `node_index_t`: a 64-bit unsigned integer type used to represent node indices.

Sub-Components:

- `loop_horizons`: a loop that iterates over the levels of the graph, starting from the starting node and exploring the graph level by level.
- `loop_nodes`: a loop that iterates over the nodes in the current level, adding unmarked neighbors to the next level.
- `loop_neighbors`: a loop that iterates over the edges connected to a node, marking unmarked neighbors and updating the level counts.

## bfs_queue

An implementation of the Breadth-First Search (BFS) algorithm for graph traversal. The algorithm explores a graph level by level, starting from a given starting node, and computes the shortest distance from the starting node to all other nodes in the graph. The design is optimized for parallel execution on multi-core CPUs and GPUs.

Top-Level Function: `bfs`

Inputs:

- `nodes`: an array of `node_t` structures, each representing a node in the graph, with `edge_begin` and `edge_end` fields indicating the range of edges connected to the node.
- `edges`: an array of `edge_t` structures, each representing an edge in the graph, with a `dst` field indicating the destination node of the edge.
- `starting_node`: a `node_index_t` value indicating the starting node of the BFS traversal.
- `level`: an array of `level_t` values, where `level[i]` represents the shortest distance from the starting node to node `i`.
- `level_counts`: an array of `edge_index_t` values, where `level_counts[i]` represents the number of nodes at distance `i` from the starting node.

Outputs:

- `level`: the updated array of shortest distances from the starting node to all nodes in the graph.
- `level_counts`: the updated array of node counts at each distance level.

Important Data Structures and Data Types:

- `node_t`: a struct representing a node in the graph, with `edge_begin` and `edge_end` fields indicating the range of edges connected to the node.
- `edge_t`: a struct representing an edge in the graph, with a `dst` field indicating the destination node of the edge.
- `level_t`: an 8-bit signed integer type representing the shortest distance from the starting node to a node.
- `node_index_t` and `edge_index_t`: 64-bit unsigned integer types representing node and edge indices, respectively.

Sub-Components:

- `queue`: a circular buffer implemented using a fixed-size array, used to store nodes to be processed in the BFS traversal.
- `init_levels`: a component that initializes the `level` array with maximum values.
- `init_horizons`: a component that initializes the `level_counts` array with zero values.
- `loop_queue`: a component that iterates over the nodes in the queue, processing each node and its neighbors.
- `loop_neighbors`: a component that iterates over the edges connected to a node, updating the `level` and `level_counts` arrays as necessary.

## fft_strided

An implementation of a FFT (Fast Fourier Transform) kernel based on the Cooley-Tukey algorithm, a divide-and-conquer approach to efficiently compute the discrete Fourier transform of a sequence. The design takes advantage of the strided memory access pattern to optimize data reuse and reduce memory bandwidth requirements. The kernel operates on complex-valued input data, represented as separate real and imaginary components, and produces the transformed output in the same format.

Top-Level Function: `fft`

Inputs:

- `real`: an array of `FFT_SIZE` (1024) `double` values representing the real component of the input sequence.
- `img`: an array of `FFT_SIZE` (1024) `double` values representing the imaginary component of the input sequence.
- `real_twid`: an array of `FFT_SIZE/2` (512) `double` values representing the real component of the twiddle factors.
- `img_twid`: an array of `FFT_SIZE/2` (512) `double` values representing the imaginary component of the twiddle factors.

Outputs:

- The transformed real and imaginary components are stored in the input arrays `real` and `img`, respectively.

Important Data Structures and Data Types:

- `double`: a 64-bit floating-point data type used to represent the real and imaginary components of the input sequence and twiddle factors.
- `FFT_SIZE`: a constant integer value (1024) representing the size of the input sequence.

Sub-Components:

- The outer loop (`outer`) iterates over the span of the input sequence, dividing it into smaller segments for processing.
- The inner loop (`inner`) iterates over the odd indices of the input sequence, performing the butterfly operation to combine adjacent elements.
- The twiddle factor multiplication component performs the complex multiplication of the input elements with the precomputed twiddle factors.

## fft_transpose

An implementation of a 1D Fast Fourier Transform (FFT) algorithm for a 512-point input signal. The algorithm is based on the Cooley-Tukey FFT algorithm and is optimized for parallel execution on a GPU architecture. The kernel function takes two input arrays, `work_x` and `work_y`, each of size 512, representing the real and imaginary parts of the input signal, respectively. The function performs a series of complex multiplications, additions, and twiddle factor calculations to transform the input signal into the frequency domain.

Top-Level Function: `fft1D_512`

Inputs:

- `work_x`: an array of 512 `TYPE` elements representing the real part of the input signal
- `work_y`: an array of 512 `TYPE` elements representing the imaginary part of the input signal

Outputs:

- `work_x`: an array of 512 `TYPE` elements representing the real part of the output signal in the frequency domain
- `work_y`: an array of 512 `TYPE` elements representing the imaginary part of the output signal in the frequency domain

Important Data Structures and Data Types:

- `TYPE`: a data type representing a double-precision floating-point number
- `complex_t`: a struct representing a complex number with real and imaginary parts of type `TYPE`

Sub-Components:

- `twiddles8`: a function that calculates the twiddle factors for an 8-point FFT
- `FFT8`: a function that performs an 8-point FFT on a complex input signal
- `loadx8` and `loady8`: functions that load 8 complex numbers from an input array into a local array
- `FF2` and `FFT4`: functions that perform 2-point and 4-point FFTs, respectively, on a complex input signal

## gemm_blocked

An implementation of the General Matrix-Matrix Multiplication (GEMM) algorithm, optimized for cache performance using a blocked algorithm. The design takes advantage of spatial locality by dividing the input matrices into smaller blocks, reducing memory access patterns and improving data reuse. The kernel performs a matrix-matrix multiplication operation, computing the product of two input matrices `m1` and `m2` and storing the result in the output matrix `prod`.

Top-Level Function: `bbgemm`

Inputs:

- `m1`: a 2D matrix of size `N x N` (where `N = row_size * col_size`) containing the first input matrix, stored in row-major order with each element of type `TYPE` (double precision floating-point).
- `m2`: a 2D matrix of size `N x N` containing the second input matrix, stored in row-major order with each element of type `TYPE` (double precision floating-point).

Outputs:

- `prod`: a 2D matrix of size `N x N` containing the product of the input matrices, stored in row-major order with each element of type `TYPE` (double precision floating-point).

Important Data Structures and Data Types:

- `TYPE`: a double precision floating-point data type, used to represent the elements of the input and output matrices.
- `block_size`: an integer constant defining the size of the blocks used in the blocked algorithm, set to 8.
- `row_size` and `col_size`: integer constants defining the size of the input matrices, set to 64.
- `N`: an integer constant representing the total number of elements in the input matrices, calculated as `row_size * col_size`.

Sub-Components:

- `loopjj` and `loopkk`: nested loops that iterate over the blocks of the input matrices, dividing the computation into smaller, cache-friendly chunks.
- `loopi` and `loopk`: inner loops that perform the actual matrix-matrix multiplication operation, iterating over the elements of the blocks.
- `loopj`: an inner loop that accumulates the partial products of the matrix-matrix multiplication operation.

## gemm_ncubed

An implementation of the GEMM (General Matrix-Matrix Multiplication) kernel that performs matrix multiplication on two input matrices, producing a resulting product matrix. The design is optimized for parallel execution, leveraging a nested loop structure to exploit data parallelism and reduce memory access patterns. The kernel operates on double-precision floating-point data, with a fixed matrix size of 64x64 elements.

Top-Level Function: `gemm`

Inputs:

- `m1`: A 2D matrix of size 64x64, represented as a 1D array of `double` values, with a total of 4096 elements. The matrix is stored in row-major order, with each row contiguous in memory.
- `m2`: A 2D matrix of size 64x64, represented as a 1D array of `double` values, with a total of 4096 elements. The matrix is stored in row-major order, with each row contiguous in memory.

Outputs:

- `prod`: A 2D matrix of size 64x64, represented as a 1D array of `double` values, with a total of 4096 elements. The matrix is stored in row-major order, with each row contiguous in memory.

Important Data Structures and Data Types:

- `TYPE`: A `double` data type, used to represent the elements of the input and output matrices.
- `N`: A constant integer value, representing the total number of elements in each matrix (4096).

Sub-Components:

- `outer loop`: A loop that iterates over the rows of the input matrices, with a loop counter `i` ranging from 0 to 63.
- `middle loop`: A loop that iterates over the columns of the input matrices, with a loop counter `j` ranging from 0 to 63.
- `inner loop`: A loop that performs the actual matrix multiplication, iterating over the elements of the input matrices and accumulating the products in a temporary variable `sum`.
- `matrix indexing`: A mechanism that calculates the memory addresses of the input and output matrices, using the loop counters `i`, `j`, and `k` to access the correct elements.

## kmp_kmp

An implementation of the Knuth-Morris-Pratt (KMP) string searching algorithm, which efficiently searches for a pattern within a given input string. The algorithm preprocesses the pattern to build a lookup table, known as the kmpNext table, which stores the maximum number of characters that can be skipped when a mismatch occurs. This table is then used to search for the pattern in the input string, incrementing a match counter for each occurrence found.

Top-Level Function: `kmp`

Inputs:

- `pattern`: a character array of size `PATTERN_SIZE` (4) representing the pattern to be searched for in the input string.
- `input`: a character array of size `STRING_SIZE` (32411) representing the input string to be searched.
- `kmpNext`: an integer array of size `PATTERN_SIZE` (4) used to store the preprocessed lookup table.
- `n_matches`: an integer array of size 1 used to store the number of matches found.

Outputs:

- `n_matches`: an integer array of size 1 containing the number of matches found.

Important Data Structures and Data Types:

- `kmpNext`: an integer array of size `PATTERN_SIZE` used to store the preprocessed lookup table, where each element represents the maximum number of characters that can be skipped when a mismatch occurs.
- `pattern`: a character array of size `PATTERN_SIZE` representing the pattern to be searched for in the input string.
- `input`: a character array of size `STRING_SIZE` representing the input string to be searched.

Sub-Components:

- `CPF` (Compute Failure Pattern): a sub-component responsible for preprocessing the pattern to build the kmpNext table. It iterates through the pattern, comparing characters and updating the kmpNext table accordingly.
- `kmp` (Knuth-Morris-Pratt): the main sub-component responsible for searching for the pattern in the input string using the preprocessed kmpNext table. It iterates through the input string, comparing characters and incrementing the match counter when a match is found.

## md_grid

An implementation of a molecular dynamics simulation. The algorithm iterates over a 3D grid of blocks, where each block contains a set of points. For each point in a block, it computes the Lennard-Jones potential with all points in neighboring blocks, and updates the force acting on the point accordingly. The design uses a block-based parallelization approach to exploit spatial locality and reduce memory access patterns.

Top-Level Function: `md`

Inputs:

- `n_points`: a 3D array of integers, where `n_points[i][j][k]` represents the number of points in block `(i, j, k)`. Each element is a 32-bit integer.
- `position`: a 4D array of `dvector_t` structures, where `position[i][j][k][l]` represents the position of point `l` in block `(i, j, k)`. Each `dvector_t` structure contains three `TYPE` (double) fields: `x`, `y`, and `z`.
- `force`: a 4D array of `dvector_t` structures, where `force[i][j][k][l]` represents the force acting on point `l` in block `(i, j, k)`. Each `dvector_t` structure contains three `TYPE` (double) fields: `x`, `y`, and `z`.

Outputs:

- `force`: the updated force array, where each element `force[i][j][k][l]` represents the new force acting on point `l` in block `(i, j, k)`.

Important Data Structures and Data Types:

- `dvector_t`: a structure containing three `TYPE` (double) fields: `x`, `y`, and `z`, used to represent 3D vectors.
- `ivector_t`: a structure containing three 32-bit integer fields: `x`, `y`, and `z`, used to represent 3D integer vectors.
- `TYPE`: a type definition for `double`, used to represent floating-point numbers.

Sub-Components:

- `loop_grid0`: a set of three nested loops that iterate over the 3D grid of blocks.
- `loop_grid1`: a set of three nested loops that iterate over the 3x3x3 cube of blocks around a given block.
- `loop_p`: a loop that iterates over the points in a block.
- `loop_q`: a loop that iterates over the points in a neighboring block.

## md_knn

An implementation of the molecular dynamics kernel, which computes the forces between atoms in a molecular system. The kernel is based on the Lennard-Jones potential and is optimized for parallel execution. The design takes into account the positions of atoms and their neighbors, calculates the distances and forces between them, and updates the forces accordingly.

Top-Level Function: `md_kernel`

Inputs:

- `force_x`: an array of `nAtoms` elements of type `TYPE` (double) representing the x-components of the forces on each atom.
- `force_y`: an array of `nAtoms` elements of type `TYPE` (double) representing the y-components of the forces on each atom.
- `force_z`: an array of `nAtoms` elements of type `TYPE` (double) representing the z-components of the forces on each atom.
- `position_x`: an array of `nAtoms` elements of type `TYPE` (double) representing the x-coordinates of each atom.
- `position_y`: an array of `nAtoms` elements of type `TYPE` (double) representing the y-coordinates of each atom.
- `position_z`: an array of `nAtoms` elements of type `TYPE` (double) representing the z-coordinates of each atom.
- `NL`: a 2D array of `nAtoms` x `maxNeighbors` elements of type `int32_t` representing the indices of the neighboring atoms for each atom.

Outputs:

- `force_x`: updated array of `nAtoms` elements of type `TYPE` (double) representing the x-components of the forces on each atom.
- `force_y`: updated array of `nAtoms` elements of type `TYPE` (double) representing the y-components of the forces on each atom.
- `force_z`: updated array of `nAtoms` elements of type `TYPE` (double) representing the z-components of the forces on each atom.

Important Data Structures and Data Types:

- `TYPE`: a type definition for `double` precision floating-point numbers.
- `nAtoms`: a constant integer value representing the number of atoms in the system (256).
- `maxNeighbors`: a constant integer value representing the maximum number of neighbors for each atom (16).
- `lj1` and `lj2`: constant values representing the Lennard-Jones coefficients.

Sub-Components:

- `loop_i`: a loop that iterates over each atom in the system, computing the forces between the current atom and its neighbors.
- `loop_j`: a nested loop that iterates over each neighbor of the current atom, computing the distance and force between the two atoms.
- `force calculation`: a component that computes the force between two atoms based on the Lennard-Jones potential.
- `force update`: a component that updates the forces on each atom based on the computed forces from its neighbors.

## nw_nw

An implementation of the Needleman-Wunsch algorithm for global pairwise sequence alignment. The algorithm is a dynamic programming approach that finds the optimal alignment between two input sequences, SEQA and SEQB, by maximizing the similarity score between the two sequences. The design consists of two main stages: matrix filling and traceback. In the matrix filling stage, the design computes the similarity scores between the input sequences and stores them in a 2D matrix M. In the traceback stage, the design traces back the optimal alignment path from the filled matrix and generates the aligned sequences.

Top-Level Function: `needwun`

Inputs:

- `SEQA`: a 1D array of characters representing the first input sequence, with a length of ALEN (128) characters.
- `SEQB`: a 1D array of characters representing the second input sequence, with a length of BLEN (128) characters.
- `alignedA`: a 1D array of characters to store the aligned sequence A, with a length of ALEN+BLEN characters.
- `alignedB`: a 1D array of characters to store the aligned sequence B, with a length of ALEN+BLEN characters.
- `M`: a 2D array of integers to store the similarity scores, with a size of (ALEN+1) x (BLEN+1).
- `ptr`: a 2D array of characters to store the traceback pointers, with a size of (ALEN+1) x (BLEN+1).

Outputs:

- `alignedA`: the aligned sequence A, stored in the input array.
- `alignedB`: the aligned sequence B, stored in the input array.

Important Data Structures and Data Types:

- `M`: a 2D array of integers to store the similarity scores, with a size of (ALEN+1) x (BLEN+1). Each element in the array represents the maximum similarity score between the subsequences of SEQA and SEQB.
- `ptr`: a 2D array of characters to store the traceback pointers, with a size of (ALEN+1) x (BLEN+1). Each element in the array represents the direction of the optimal alignment path.

Sub-Components:

- `init_row` and `init_col`: initialization loops to set the boundary values of the matrix M.
- `fill_out` and `fill_in`: nested loops to fill the matrix M with similarity scores.
- `trace`: a loop to trace back the optimal alignment path from the filled matrix and generate the aligned sequences.
- `pad_a` and `pad_b`: loops to pad the aligned sequences with underscores to ensure a fixed length of ALEN+BLEN characters.

## sort_merge

An implementation of the merge sort algorithm, a divide-and-conquer approach to sorting an array of elements. The design takes an array of integers as input and produces a sorted array as output. The algorithm works by recursively dividing the input array into smaller subarrays, sorting each subarray, and then merging the sorted subarrays to produce the final sorted array.

Top-Level Function: `ms_mergesort`

Inputs:

- `a`: an array of `SIZE` elements of type `TYPE` (int32_t), representing the input array to be sorted.

Outputs:

- `a`: the sorted array of `SIZE` elements of type `TYPE` (int32_t), representing the output of the merge sort algorithm.

Important Data Structures and Data Types:

- `TYPE`: an integer data type (int32_t) used to represent the elements of the input array.
- `SIZE`: a constant integer value (2048) representing the size of the input array.
- `temp`: a temporary array of `SIZE` elements of type `TYPE` used to store intermediate results during the merge process.

Sub-Components:

- `merge`: a sub-component that implements the merge step of the merge sort algorithm, taking three indices (`start`, `m`, and `stop`) and the input array `a` as inputs, and producing a merged and sorted subarray as output.
- The `merge` sub-component consists of three loops: `merge_label1` and `merge_label2` copy the left and right halves of the input array into a temporary array, respectively, and `merge_label3` merges the two halves into a single sorted array.
- The `ms_mergesort` kernel iterates over the input array, recursively dividing it into smaller subarrays, and calling the `merge` sub-component to sort and merge each subarray.

## sort_radix

An implementation of the radix sort approach to sort an array of integers. The algorithm is designed to be highly parallelizable and is optimized for execution on heterogeneous computing architectures. The kernel takes an input array `a` and sorts it in-place using a temporary buffer `b`. The sorting process is performed in multiple passes, with each pass sorting the array based on a specific radix (or digit) of the integers. The kernel uses a combination of local and global scans to efficiently sort the array.

Top-Level Function: `ss_sort`

Inputs:

- `a`: an array of `SIZE` integers to be sorted, where `SIZE` is 2048.
- `b`: a temporary array of `SIZE` integers used for sorting.
- `bucket`: an array of `BUCKETSIZE` integers used for storing the histogram of the input array, where `BUCKETSIZE` is `NUMOFBLOCKS*RADIXSIZE`.
- `sum`: an array of `SCAN_RADIX` integers used for storing the sum of the histogram.

Outputs:

- `a`: the sorted array of integers.

Important Data Structures and Data Types:

- `bucket`: an array of `BUCKETSIZE` integers used for storing the histogram of the input array. Each element of the array represents the count of integers in the input array that have a specific radix value.
- `sum`: an array of `SCAN_RADIX` integers used for storing the sum of the histogram. Each element of the array represents the cumulative sum of the counts in the `bucket` array.
- `TYPE`: an integer type defined as `int32_t`, used for representing the elements of the input array.
- `RADIXSIZE`: an integer constant defined as 4, representing the number of radix values used in the sorting process.

Sub-Components:

- `local_scan`: a function that performs a local scan of the `bucket` array to compute the cumulative sum of the counts.
- `sum_scan`: a function that performs a global scan of the `bucket` array to compute the sum of the histogram.
- `last_step_scan`: a function that updates the `bucket` array based on the sum of the histogram.
- `init`: a function that initializes the `bucket` array to zero.
- `hist`: a function that computes the histogram of the input array based on a specific radix value.
- `update`: a function that updates the input array based on the sorted histogram.

## spmv_crs

An implementation of the Sparse Matrix-Vector Multiplication (SpMV) algorithm, a fundamental operation in linear algebra and machine learning. The design takes advantage of the Compressed Row Storage (CRS) format to efficiently store and process sparse matrices. The algorithm iterates over the rows of the matrix, computing the dot product of each row with a given input vector and storing the results in an output vector.

Top-Level Function: `spmv`

Inputs:

- `val`: an array of `NNZ` elements of type `TYPE` (double precision floating point), representing the non-zero values of the sparse matrix.
- `cols`: an array of `NNZ` elements of type `int32_t`, representing the column indices of the non-zero values in the sparse matrix.
- `rowDelimiters`: an array of `N+1` elements of type `int32_t`, representing the row delimiters of the sparse matrix in CRS format.
- `vec`: an array of `N` elements of type `TYPE` (double precision floating point), representing the input vector.

Outputs:

- `out`: an array of `N` elements of type `TYPE` (double precision floating point), representing the output vector resulting from the SpMV operation.

Important Data Structures and Data Types:

- `TYPE`: a double precision floating point data type, used to represent the non-zero values of the sparse matrix and the input/output vectors.
- `int32_t`: a 32-bit signed integer data type, used to represent the column indices and row delimiters of the sparse matrix.

Sub-Components:

- `spmv_1`: a loop that iterates over the rows of the sparse matrix, computing the dot product of each row with the input vector.
- `spmv_2`: a nested loop that iterates over the non-zero elements of each row, computing the dot product of the row with the input vector.

## spmv_ellpack

An implementation the ELLPACK sparse matrix-vector multiplication algorithm. This algorithm is optimized for sparse matrices with a small number of non-zero elements per row. The design takes advantage of the sparse structure of the matrix to reduce memory access and improve performance. The kernel computes the matrix-vector product of a sparse matrix and a dense vector, storing the result in an output vector.

Top-Level Function: `ellpack`

Inputs:

- `nzval`: a 2D array of size N x L, where N is the number of rows in the sparse matrix and L is the maximum number of non-zero elements per row. Each element is of type `TYPE` (double precision floating point). The array stores the non-zero values of the sparse matrix.
- `cols`: a 2D array of size N x L, where N is the number of rows in the sparse matrix and L is the maximum number of non-zero elements per row. Each element is of type `int32_t`. The array stores the column indices of the non-zero elements in the sparse matrix.
- `vec`: a 1D array of size N, where N is the number of rows in the sparse matrix. Each element is of type `TYPE` (double precision floating point). The array stores the dense vector to be multiplied with the sparse matrix.

Outputs:

- `out`: a 1D array of size N, where N is the number of rows in the sparse matrix. Each element is of type `TYPE` (double precision floating point). The array stores the result of the matrix-vector product.

Important Data Structures and Data Types:

- `TYPE`: a double precision floating point data type used to represent the elements of the sparse matrix and the dense vector.
- `int32_t`: a 32-bit integer data type used to represent the column indices of the non-zero elements in the sparse matrix.

Sub-Components:

- `ellpack_1`: a loop that iterates over the rows of the sparse matrix, computing the dot product of each row with the dense vector.
- `ellpack_2`: a nested loop that iterates over the non-zero elements of each row, computing the product of each non-zero element with the corresponding element of the dense vector and accumulating the results.

## stencil_stencil2d

An implementation of a 2D stencil computation that applies a 3x3 filter to a 2D input array, producing a 2D output array. The kernel iterates over the input array, applying the filter to each element and its neighbors, and accumulates the results to produce the output array. The kernel is designed to perform a single iteration of the stencil computation.

Top-Level Function: `stencil`

Inputs:

- `orig`: a 2D array of `TYPE` (int32_t) elements, representing the input data, with a size of `row_size` x `col_size` (128x64).
- `sol`: a 2D array of `TYPE` (int32_t) elements, representing the output data, with a size of `row_size` x `col_size` (128x64).
- `filter`: a 1D array of `TYPE` (int32_t) elements, representing the 3x3 filter, with a size of `f_size` (9).

Outputs:

- `sol`: the output 2D array, with the same size and data type as the input `sol` array.

Important Data Structures and Data Types:

- `TYPE`: an alias for `int32_t`, representing the data type of the input and output arrays.
- `row_size` and `col_size`: constants defining the size of the input and output arrays.
- `f_size`: a constant defining the size of the filter array.

Sub-Components:

- The kernel consists of four nested loops: two outer loops iterating over the rows and columns of the input array, and two inner loops iterating over the elements of the filter. The inner loops perform the stencil computation, accumulating the results in a temporary variable `temp`.
- The kernel uses a temporary variable `mul` to store the product of the filter element and the corresponding input element.
- The kernel uses a label `stencil_label1` to `stencil_label4` to identify the loops and facilitate debugging and optimization.

## stencil_stencil3d

An implementation of a 3D stencil computation algorithm, as described in the paper "Stencil computation optimization and auto-tuning on state-of-the-art multicore architectures" by K. Datta et al. The kernel takes a 3D array of input values, applies a stencil operation to each element, and produces a 3D array of output values. The stencil operation involves computing a weighted sum of neighboring elements, where the weights are stored in a coefficient array. The kernel also handles boundary conditions by filling the output array with original values at the boundaries.

Top-Level Function: `stencil3d`

Inputs:

- `C`: a 1D array of two coefficients, `C[0]` and `C[1]`, of type `int32_t`, used for weighting the stencil operation.
- `orig`: a 3D array of input values, of size `SIZE` (row_size x col_size x height_size), of type `int32_t`, representing the original data.
- `sol`: a 3D array of output values, of size `SIZE` (row_size x col_size x height_size), of type `int32_t`, representing the solution.

Outputs:

- `sol`: the 3D array of output values, of size `SIZE` (row_size x col_size x height_size), of type `int32_t`, representing the solution.

Important Data Structures and Data Types:

- `TYPE`: an alias for `int32_t`, used to represent the data type of the input and output arrays.
- `SIZE`: a constant representing the total size of the 3D array, computed as `row_size * col_size * height_size`.
- `INDX`: a macro used to compute the index of an element in the 3D array, given its row, column, and height indices.

Sub-Components:

- Boundary condition handling: a set of nested loops that fill the output array with original values at the boundaries.
- Stencil computation: a set of nested loops that apply the stencil operation to each element of the input array, using the coefficient array and the original values.

## viterbi_viterbi

An implementation fo the the Viterbi algorithm, a dynamic programming approach to find the most likely state sequence in a Hidden Markov Model (HMM) given a sequence of observations. The algorithm iteratively computes the probabilities of being in each state at each time step, and then backtracks to recover the most likely state sequence.

Top-Level Function: `viterbi`

Inputs:

- `obs`: an array of `N_OBS` tokens, each of type `tok_t` (uint8_t), representing the sequence of observations.
- `init`: an array of `N_STATES` initial probabilities, each of type `prob_t` (double), representing the probability of being in each state initially.
- `transition`: a 2D array of `N_STATES` x `N_STATES` transition probabilities, each of type `prob_t` (double), representing the probability of transitioning from one state to another.
- `emission`: a 2D array of `N_STATES` x `N_TOKENS` emission probabilities, each of type `prob_t` (double), representing the probability of observing a token in each state.
- `path`: an array of `N_OBS` states, each of type `state_t` (uint8_t), to store the most likely state sequence.

Outputs:

- `path`: the most likely state sequence, stored in the input array.

Important Data Structures and Data Types:

- `prob_t`: a double-precision floating-point type used to represent probabilities in -log space.
- `tok_t`: an unsigned 8-bit integer type used to represent tokens.
- `state_t`: an unsigned 8-bit integer type used to represent states.
- `step_t`: a 32-bit signed integer type used to represent time steps.
- `llike`: a 2D array of `N_OBS` x `N_STATES` probabilities, each of type `prob_t`, used to store the likelihood of being in each state at each time step.

Sub-Components:

- `L_init`: a loop that initializes the likelihood array with the first observation and initial probabilities.
- `L_timestep`: a loop that iteratively computes the probabilities over time.
- `L_curr_state`: a loop that computes the likelihood of being in each state at each time step.
- `L_prev_state`: a loop that computes the likelihood of transitioning from each previous state to the current state.
- `L_end`: a loop that identifies the end state with the highest probability.
- `L_backtrack`: a loop that backtracks to recover the full path by finding the most likely previous state at each time step.

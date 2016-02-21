#### Benchmark Test

##### Sample Commands
  * Single Iteration Single Process
  ```sh
  python ndstore_benchmark.py kasthuri11 image 5 --server localhost:8000
  ```
  * 13 Iterations Single Process
  ```sh
  python ndstore_benchmark.py kasthuri11 image 5 --server localhost:8000 --iter 13
  ```
  * 13 Iterations 2 Processes
  ```sh
  python ndstore_benchmark.py kasthuri11 image 5 --server localhost:8000 --iter 13 --num 2
  ```

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
  * 13 iterations 16 processes offset 3000,3000,0
  ```sh
  python ndstore_benchmark.py --server localhost:8000 kasthuri11 image 0 --iter 13 --num 16 --offset 3000 3000 0  
  ```
  * Write Tests
  ```sh
  python ndstore_benchmark.py kasthuri11 image 5 --iter 1 --write True --server localhost:8000 --num 2
  ```

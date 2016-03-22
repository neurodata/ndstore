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

##### Commands for benchmark tests
  * Read Tests
  ```sh
  sudo python ndstore_benchmark_new.py kasthuri11 image 0 --iter 5 --size 13 --offset 3000 3000 0 --num 1
  sudo python ndstore_benchmark_new.py kasthuri11 image 0 --iter 5 --size 13 --offset 3000 3000 0 --num 2
  sudo python ndstore_benchmark_new.py kasthuri11 image 0 --iter 5 --size 13 --offset 3000 3000 0 --num 4
  sudo python ndstore_benchmark_new.py kasthuri11 image 0 --iter 5 --size 13 --offset 3000 3000 0 --num 8
  sudo python ndstore_benchmark_new.py kasthuri11 image 0 --iter 5 --size 13 --offset 3000 3000 0 --num 16
  ```
  * Write Tests
  ```sh
  sudo python ndstore_benchmark_new.py kasthuri11 image 0 --iter 5 --size 13 --offset 3000 3000 0 --num 1 --write True
  sudo python ndstore_benchmark_new.py kasthuri11 image 0 --iter 5 --size 13 --offset 3000 3000 0 --num 2 --write True
  sudo python ndstore_benchmark_new.py kasthuri11 image 0 --iter 5 --size 13 --offset 3000 3000 0 --num 4 --write True
  sudo python ndstore_benchmark_new.py kasthuri11 image 0 --iter 5 --size 13 --offset 3000 3000 0 --num 8 --write True
  sudo python ndstore_benchmark_new.py kasthuri11 image 0 --iter 5 --size 13 --offset 3000 3000 0 --num 16 --write True
  ```

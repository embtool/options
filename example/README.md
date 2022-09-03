# Toggle Example

## Table of Contents

- [Quick-start with manual compilation](#quick-start-with-manual-compilation)
- [Quick-start with CMake](#quick-start-with-cmake)

# Quick-start with manual compilation

- Generate Toggle files in include/ and src/ using files in yaml/.

```console
$ ../generate.py
```

- Compile (should warn about using default CHAR_ID).
- Execute.

```console
$ gcc -o main main.c src/toggle.c -I include/
... "CHAR_ID is not defined. Using default." ...

$ ./main
DEBUG: main: begin
+----------------+
|LCD 16x2        |
|                |
+----------------+
TEST: main: changing display from 16x2 to 20x4
+--------------------+
|LCD 20x4            |
|                    |
|                    |
|                    |
+--------------------+
DEBUG: main: end
```

- Compile defining CHAR_ID to select the characterization for tests.
- Execute.

```console
$ gcc -o main main.c src/toggle.c -I include/ -D CHAR_ID=CHAR_ID_TEST
$ ./main
DEBUG: main: begin
+----------------+
|LCD 16x2        |
|                |
+----------------+
TEST: main: changing display from 16x2 to 20x4
+--------------------+
|LCD 20x4            |
|                    |
|                    |
|                    |
+--------------------+
DEBUG: main: end
```

- Compile defining CHAR_ID to select the characterization version 1.
- Execute.

```console
$ gcc -o main main.c src/toggle.c -I include/ -D CHAR_ID=CHAR_ID_V1
$ ./main
+----------------+
|LCD 16x2        |
|                |
+----------------+
```

- Compile selecting the characterization version 2.
- Execute.

```console
$ gcc -o main main.c src/toggle.c -I include/ -D CHAR_ID=CHAR_ID_V2
$ ./main
+--------------------+
|LCD 20x4            |
|                    |
|                    |
|                    |
+--------------------+
```

# Quick-start with CMake

- Compile defining CHAR_ID to select the characterization for tests.
- Execute.

```console
$ cmake -B build/ -D CHAR_ID=CHAR_ID_TEST
$ cmake --build build/
$ ./build/main
DEBUG: main: begin
+----------------+
|LCD 16x2        |
|                |
+----------------+
TEST: main: changing display from 16x2 to 20x4
+--------------------+
|LCD 20x4            |
|                    |
|                    |
|                    |
+--------------------+
DEBUG: main: end
```

- Compile defining CHAR_ID to select the characterization version 1.
- Execute.

```console
$ cmake -B build/ -D CHAR_ID=CHAR_ID_V1
$ cmake --build build/
$ ./build/main
+----------------+
|LCD 16x2        |
|                |
+----------------+
```

- Compile defining CHAR_ID to select the characterization version 2.
- Execute.

```console
$ cmake -B build/ -D CHAR_ID=CHAR_ID_V2
$ cmake --build build/
$ ./build/main
+--------------------+
|LCD 20x4            |
|                    |
|                    |
|                    |
+--------------------+
```

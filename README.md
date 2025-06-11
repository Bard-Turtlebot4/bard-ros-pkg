# bard-ros-pkg

All scripts written for Turtlebot4

## Building instructions

To use these packages, first clone the repository and use Colcon to build packages. First call

```bash
$ colcon build --symlink-install --packages-select name_of_package
```
Then install packages with

```bash
$ source install/local_setup.bash
```
To run packages, use

```bash
$ ros2 run name_of_package name_of_node
```

### Example

```bash
$ colcon build --symlink-install --packages-select bsripkg_lightring
$ source install/local_setup.bash
$ ros2 run bsrippkg_lightring bsri_node_lightring_test
```


# Android runtime profiler

This profiler targets a custom built AOSP (version `8.1.0_r52`). The profiler has been test on Nexus 6P.

## Requirements

- `rogcat`: a `adb logcat` wrapper providing some nice utilities

## How to use

The basic use case of this profiler is:

- Connecting your device to the computer
- Using `rogcat` to capture system logs
- Using `profiler.py` to generate a nice diagram

```shell
> rogcat -f json -o <trace_file_path>
> ./profiler.py <trace-file-path> <pid>
```

## QA

- How do I find out the pid?

    ```shell
    > adb shell ps | grep <package-name>
    ```

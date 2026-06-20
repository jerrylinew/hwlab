"""OpenCV acceleration setup."""

import cv2


def init_acceleration() -> str:
    """Enable OpenCV OpenCL when available and return the active backend."""
    try:
        if not cv2.ocl.haveOpenCL():
            return "CPU (OpenCL unavailable)"

        cv2.ocl.setUseOpenCL(True)
        if not cv2.ocl.useOpenCL():
            return "CPU (OpenCL disabled)"

        try:
            device = cv2.ocl.Device_getDefault()
            device_name = device.name() if device else "default device"
        except Exception:
            device_name = "default device"
        return f"OpenCL ({device_name})"
    except Exception as exc:
        return f"CPU (OpenCL init failed: {exc})"

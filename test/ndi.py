import sys
import numpy as np
import cv2
import NDIlib as ndi
import time


def ndi_init():
    """
    NDI init
    :return:
    """

    if not ndi.initialize():
        return 0

    ndi_find = ndi.find_create_v2()

    if ndi_find is None:
        return 0

    sources = []
    target_source = None
    #while not len(sources) > 0:
    for i in range(10):
        ndi.find_wait_for_sources(ndi_find, 100)
        sources = ndi.find_get_current_sources(ndi_find)
        for i, s in enumerate(sources):
            if "OBS" in s.ndi_name:
                target_source = sources[i]

    ndi_recv_create = ndi.RecvCreateV3()
    ndi_recv_create.color_format = ndi.RECV_COLOR_FORMAT_BGRX_BGRA
    ndi_recv = ndi.recv_create_v3(ndi_recv_create)

    if ndi_recv is None:
        return 0
    ndi.recv_connect(ndi_recv, target_source)
    ndi.find_destroy(ndi_find)

    return ndi_recv


def env_close(ndi_recv):
    """
    env close
    :param ndi_recv:
    :return:
    """
    ndi.recv_destroy(ndi_recv)
    ndi.destroy()
    cv2.destroyAllWindows()


def main():

    count = 0
    start = time.time()
    ndi_recv = ndi_init()

    while True:
        t, v, _, _ = ndi.recv_capture_v2(ndi_recv, 5000)
        if t == ndi.FRAME_TYPE_VIDEO:
            count += 1
            end = time.time()
            fps =int(count / (end - start))
            frame = v.data
            shape = frame.shape
            #frame = np.copy(v.data)
            cv2.putText(frame, "FPS:" + str(fps), (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            cv2.putText(frame, str(shape), (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            cv2.imshow('ndi image', frame)
            ndi.recv_free_video_v2(ndi_recv, v)

        if cv2.waitKey(1) & 0xff == 27:
            break

    env_close(ndi_recv)

    return 0


if __name__ == "__main__":
    #sys.exit(main())
    main()


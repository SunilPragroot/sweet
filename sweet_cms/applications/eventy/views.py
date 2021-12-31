import os

from flask import Blueprint, render_template, Response

from libs.sweet_theming import themed_template
from sweet_cms.applications.eventy.models import Programme, ProgrammeFile

import cv2
import threading


blueprint = Blueprint("eventy", __name__, static_folder="./static", template_folder='templates')


@blueprint.route('/event/<string:event_slug>')
def event(event_slug):
    from sweet_cms.models import Event
    programme= Programme.query.all()
    event = Event.query.filter_by(slug=event_slug).first_or_404()
    return render_template(themed_template('eventy/event.html', 'web'), event=event,programme=programme)


@blueprint.route('/event/stream/<event_slug>')
def event_stream(event_slug):
    from sweet_cms.models import Programme, Event
    import datetime
    from libs.sweet_apps import get_sweet_app
    from flask import current_app
    eventy_app = get_sweet_app('Eventy')
    event = Event.query.filter_by(slug=event_slug).first()
    stream_playlist = ""
    if event:
        current_app.logger.info("Found Event {}".format(event.id))
        programme_streaming = event.programmes.filter(Programme.end_time >= datetime.datetime.now()).first()
        if programme_streaming:
            current_app.logger.info("Found Programme {}".format(programme_streaming.id))
            videos = programme_streaming.videos
            if videos:
                current_app.logger.info("Found {} Videos".format(len(videos)))
                video_streaming = videos[0]
                if video_streaming.file_status == 'ready':
                    current_app.logger.info("Found video {}".format(programme_streaming.id))
                    file_path = video_streaming.file_url
                    file_path = os.path.join(eventy_app.app_path, current_app.config['EVENTY_UPLOADS_DIR'], file_path)
                    file_dir = os.path.dirname(file_path)
                    file_name = os.path.basename(file_path)
                    bare_file_name = '.'.join(file_name.split('.')[:-1])
                    playlist_path = os.path.join(file_dir, f"{bare_file_name}.m3u8")
                    current_app.logger.info("Found playlist {}".format(playlist_path))
                    stream_playlist = open(playlist_path).read()
                    return Response(stream_playlist,
                                    mimetype='application/x-mpegURL')
    return Response(stream_playlist, mimetype='application/x-mpegURL')


  # 3shubvham
  # ##############>>>>>>>>>>>.......................................
video_camera = None
global_frame = None


@blueprint.route('/record_status', methods=['POST'])
def record_status():
    global video_camera
    if video_camera == None:
        video_camera = VideoCamera()

    json = request.get_json()

    status = json['status']

    if status == "true":
        video_camera.start_record()
        return jsonify(result="started")
    else:
        video_camera.stop_record()
        return jsonify(result="stopped")

def video_stream():
    global video_camera
    global global_frame

    if video_camera == None:
        video_camera = VideoCamera()

    while True:
        frame = video_camera.get_frame()

        if frame != None:
            global_frame = frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
          pass

@blueprint.route('/video_viewer')
def video_viewer():
    return Response(video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
##################################################################
class RecordingThread (threading.Thread):
    def __init__(self, name, camera):
        threading.Thread.__init__(self)
        self.name = name
        self.isRunning = True

        self.cap = camera
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.out = cv2.VideoWriter('./static/video.avi', fourcc, 20.0, (640, 480))

    def run(self):
        while self.isRunning:
            ret, frame = self.cap.read()
            if ret:
                self.out.write(frame)

        self.out.release()

    def stop(self):
        self.isRunning = False

    def __del__(self):
        self.out.release()

class VideoCamera(object):
    def __init__(self):
        # Open a camera
        self.cap = cv2.VideoCapture(0)

        # Initialize video recording environment
        self.is_record = False
        self.out = None

        # Thread for recording
        self.recordingThread = None

    def __del__(self):
        self.cap.release()

    def get_frame(self):
        ret, frame = self.cap.read(0)

        if ret:
            ret, jpeg = cv2.imencode('.jpg', frame)

            # Record video
            # if self.is_record:
            #     if self.out == None:
            #         fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            #         self.out = cv2.VideoWriter('./static/video.avi',fourcc, 20.0, (640,480))

            #     ret, frame = self.cap.read()
            #     if ret:
            #         self.out.write(frame)
            # else:
            #     if self.out != None:
            #         self.out.release()
            #         self.out = None

            return jpeg.tobytes()

        else:
            return None

    def start_record(self):
        self.is_record = True
        self.recordingThread = RecordingThread("Video Recording Thread", self.cap)
        self.recordingThread.start()

    def stop_record(self):
        self.is_record = False

        if self.recordingThread != None:
            self.recordingThread.stop()

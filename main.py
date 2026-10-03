import socket
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

PORT = 5000

class ChatApp(App):
    def build(self):
        self.sock = None
        self.connected = False
        self.buffer = b""

        root = BoxLayout(orientation="vertical", padding=10, spacing=8)

        top = BoxLayout(size_hint_y=None, height=48, spacing=8)
        self.ip_input = TextInput(hint_text="Server IP", multiline=False)
        self.connect_btn = Button(text="Connect")
        self.connect_btn.bind(on_press=self.toggle_connection)
        top.add_widget(self.ip_input)
        top.add_widget(self.connect_btn)
        root.add_widget(top)

        self.status = Label(text="Disconnected", size_hint_y=None, height=35)
        root.add_widget(self.status)

        self.messages = Label(text="", size_hint_y=None, halign="left", valign="top")
        self.messages.bind(texture_size=self._update_message_size)
        self.scroll = ScrollView()
        self.scroll.add_widget(self.messages)
        root.add_widget(self.scroll)

        bottom = BoxLayout(size_hint_y=None, height=48, spacing=8)
        self.message_input = TextInput(hint_text="Message", multiline=False)
        self.message_input.bind(on_text_validate=self.send_message)
        send_btn = Button(text="Send", size_hint_x=None, width=90)
        send_btn.bind(on_press=self.send_message)
        bottom.add_widget(self.message_input)
        bottom.add_widget(send_btn)
        root.add_widget(bottom)
        return root

    def _update_message_size(self, *_):
        self.messages.height = max(self.messages.texture_size[1], 40)
        self.messages.text_size = (max(self.scroll.width - 20, 40), None)

    def add_message(self, text):
        def update(_):
            self.messages.text = (self.messages.text + "\n" if self.messages.text else "") + text
            self._update_message_size()
            self.scroll.scroll_y = 0
        Clock.schedule_once(update, 0)

    def toggle_connection(self, *_):
        self.disconnect() if self.connected else self.connect()

    def connect(self):
        ip = self.ip_input.text.strip()
        if not ip:
            self.status.text = "Enter server IP"
            return
        self.status.text = "Connecting..."
        threading.Thread(target=self._connect_worker, args=(ip,), daemon=True).start()

    def _connect_worker(self, ip):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((ip, PORT))
            sock.settimeout(None)
            self.sock = sock
            self.connected = True
            self.buffer = b""
            Clock.schedule_once(lambda dt: self._set_connected_status(), 0)
            threading.Thread(target=self.receive_loop, daemon=True).start()
        except Exception as e:
            Clock.schedule_once(lambda dt, err=str(e): self._connection_failed(err), 0)

    def _set_connected_status(self):
        self.status.text = f"Connected to {self.ip_input.text.strip()}:{PORT}"
        self.connect_btn.text = "Disconnect"

    def _connection_failed(self, error):
        self.connected = False
        self.sock = None
        self.status.text = f"Connection failed: {error}"
        self.connect_btn.text = "Connect"

    def receive_loop(self):
        while self.connected and self.sock:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                self.buffer += data
                while b"\n" in self.buffer:
                    raw, self.buffer = self.buffer.split(b"\n", 1)
                    if raw:
                        self.add_message("Other: " + raw.decode("utf-8", errors="replace"))
            except (ConnectionResetError, BrokenPipeError, OSError):
                break
        Clock.schedule_once(lambda dt: self._remote_disconnect(), 0)

    def _remote_disconnect(self):
        if self.connected:
            self.status.text = "Connection lost"
        self.connected = False
        self.connect_btn.text = "Connect"
        try:
            if self.sock:
                self.sock.close()
        except OSError:
            pass
        self.sock = None

    def send_message(self, *_):
        if not self.connected or not self.sock:
            self.status.text = "Not connected"
            return
        message = self.message_input.text.strip()
        if not message:
            return
        try:
            self.sock.sendall((message + "\n").encode("utf-8"))
            self.add_message("You: " + message)
            self.message_input.text = ""
        except (ConnectionResetError, BrokenPipeError, OSError):
            self._remote_disconnect()

    def disconnect(self):
        self.connected = False
        try:
            if self.sock:
                self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            if self.sock:
                self.sock.close()
        except OSError:
            pass
        self.sock = None
        self.connect_btn.text = "Connect"
        self.status.text = "Disconnected"

    def on_stop(self):
        self.disconnect()

if __name__ == "__main__":
    ChatApp().run()

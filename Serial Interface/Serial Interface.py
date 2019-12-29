"""
Vincent Piegsa (2019)

This program is an interface for the serial communication with an Arduino.
"""


import serial
import serial.tools.list_ports
import threading
import csv

from collections import deque
import matplotlib.pyplot as plt 
import matplotlib.animation as animation
from matplotlib import style

import tkinter as tk 
from tkinter import ttk
from tkinter import messagebox as tkm

import matplotlib
from matplotlib import style
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation


matplotlib.use("TkAgg")
style.use('ggplot')


class Application(tk.Tk):

	"""
	Graphical User Interface (GUI)
	
	Attributes:
	    ax1 (TYPE): matplotlib graph
	    backwards_label (TYPE): moving backwards label
	    baud (TYPE): baudrate entry
	    baud_label (TYPE): baudrate label
	    canvas (TYPE): matplotlib graph canvas
	    connect (TYPE): connect button
	    connection_label (TYPE): connection label
	    fig (TYPE): matplotlib figure
	    file_entry (TYPE): entry for filename
	    file_label (TYPE): label for filename entry
	    forwards_label (TYPE): moving forwards label
	    full_label (TYPE): forwards + backwards label
	    movement_label (TYPE): movement label
	    port_label (TYPE): port label
	    port_select (TYPE): select port spinbox
	    save_label (TYPE): label for saving data
	    start_backwards (TYPE): move backwards button
	    start_forwards (TYPE): move forwards button
	    start_full (TYPE): move forwards + backwards button
	"""
	
	def __init__(self, *args, **kwargs):
		"""
		Initializes the GUI
		
		Args:
		    *args: arguments
		    **kwargs: keyword arguments
		"""

		tk.Tk.__init__(self, *args, **kwargs)
		tk.Tk.wm_title(self, 'Serial Interface')
		tk.Tk.geometry(self, '740x400')
		tk.Tk.iconbitmap(self, default='arduino.ico')

		graph = tk.Frame(self)
		graph.pack(side='left', fill='both', expand=True)

		controls = tk.Frame(self)
		controls.pack(side='right', fill='both', expand=True, padx=10, pady=10)

		connection_settings = tk.Frame(controls)
		connection_settings.pack(side='top', fill='both', expand=True)

		movement_settings = tk.Frame(controls)
		movement_settings.pack(fill='both', expand=True)

		save_settings = tk.Frame(controls)
		save_settings.pack(side='bottom', fill='both', expand=True)

		self.connection_label = ttk.Label(connection_settings, text='Connection', font=("Verdana", 11))
		self.connection_label.grid(row=0, column=0, sticky='nsew', pady=(0, 5))

		self.port_label = ttk.Label(connection_settings, text='Port')
		self.port_label.grid(row=1, column=0, sticky='nsew', padx=(0, 25), pady=2)
		self.port_select = tk.Spinbox(connection_settings, values=Utils.list_comports(), width=36)
		self.port_select.grid(row=1, column=1, columnspan=2, sticky='nsew', pady=2)

		self.baud_label = ttk.Label(connection_settings, text='Baud')
		self.baud_label.grid(row=2, column=0, sticky='nsew', padx=(0, 25), pady=5)
		self.baud = ttk.Entry(connection_settings)
		self.baud.insert(0, '115200')
		self.baud.grid(row=2, column=1, columnspan=2, sticky='nsew', pady=5)

		self.connect = ttk.Button(connection_settings, text='Connect', command=lambda: self._connect())
		self.connect.grid(row=3, column=1, columnspan=1, sticky='nsew', padx=(0, 2), pady=2)

		self.connect = ttk.Button(connection_settings, text='Disconnect', command=lambda: self._disconnect())
		self.connect.grid(row=3, column=2, columnspan=1, sticky='nsew', padx=(2, 0),pady=2)

		self.movement_label = ttk.Label(movement_settings, text='Movement', font=("Verdana", 11))
		self.movement_label.grid(row=0, column=0, sticky='nsew', pady=(0, 5))

		self.forwards_label = ttk.Label(movement_settings, text='CW')
		self.forwards_label.grid(row=1, column=0, sticky='nsew', pady=(0, 5))
		self.start_forwards = ttk.Button(movement_settings, text='0x01', command=lambda: self.send_and_recv('0x01'))
		self.start_forwards.grid(row=1, column=1, columnspan=1, sticky='nsew', padx=(5, 0), pady=(0, 5))

		self.backwards_label = ttk.Label(movement_settings, text='ACW')
		self.backwards_label.grid(row=2, column=0, sticky='nsew', pady=(0, 5))
		self.start_backwards = ttk.Button(movement_settings, text='0x02', command=lambda: self.send_and_recv('0x02'))
		self.start_backwards.grid(row=2, column=1, columnspan=1, sticky='nsew', padx=(5, 0), pady=(0, 5))

		self.full_label = ttk.Label(movement_settings, text='CW+ACW')
		self.full_label.grid(row=3, column=0, sticky='nsew', pady=(0, 5))
		self.start_full = ttk.Button(movement_settings, text='0x03', command=lambda: self.send_and_recv('0x03'))
		self.start_full.grid(row=3, column=1, columnspan=1, sticky='nsew', padx=(5, 0), pady=(0, 5))

		self.save_label = ttk.Label(save_settings, text='Data Settings', font=("Verdana", 11))
		self.save_label.grid(row=0, column=0, sticky='nsew', pady=(0, 5))

		self.file_label = ttk.Label(save_settings, text='Filename')
		self.file_label.grid(row=1, column=0, sticky='nsew', pady=(0, 5))

		self.file_entry = ttk.Entry(save_settings)
		self.file_entry.insert(0, 'data.csv')
		self.file_entry.grid(row=1, column=1, columnspan=2, pady=5)

		self.fig = Figure(figsize=(4, 5))
		self.ax1 = self.fig.add_subplot(111)
		self.ax1.get_xaxis().set_visible(False)

		self.canvas = FigureCanvasTkAgg(self.fig, self)
		self.canvas.draw()
		self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)


	def _connect(self) -> None:
		"""
		Established connection with Arduino
		"""

		try:
			port = self.get_port()
			baud = int(self.baud.get())
			file = self.file_entry.get()

			self._connection = Connection(port, baud, file)
			tkm.showinfo('Connection successful.', 'Connection with %s at %d baud has been established successfully.' % (port, baud))

		except Exception as e:
			tkm.showerror('Connection failed.', 'Failed to establish connection with %s at %d baud. Please check connection and retry.\n %s' % (port, baud, e))

	def _disconnect(self) -> None:
		"""
		Disconnect from Arduino
		"""

		try:
			self._connection.close()
			tkm.showinfo('Disconnected.', 'Disconnected successfully.')

		except Exception as e:
			tkm.showerror('Failed to disconnect.', 'Failed to disconnect. Please check connection and retry.')

	def get_port(self) -> str:
		"""
		Retrieves the selected COM-Port
		
		Returns:
		    str: COM-Port
		"""

		return self.port_select.get().split('-')[0].rstrip()

	def send_and_recv(self, data: str) -> None:
		"""
		Send movement command and receive data
		
		Args:
		    data (str): movement command
		"""

		if hasattr(self, '_connection'):

			self._connection.send(data)
			self._connection.listen()

	def animate(self, i: int) -> None:
		"""Summary
		
		Args:
		    i (int): interval
		"""

		if hasattr(self, '_connection'):

			self.ax1.clear()

			self.ax1.plot(self._connection.index, self._connection.t_env, label='T_env')
			self.ax1.plot(self._connection.index, self._connection.t1, label='T_1')
			self.ax1.plot(self._connection.index, self._connection.t2, label='T_2')

			self.ax1.legend(loc='best')


class Utils:

	"""
	A collection of used methods
	"""
	
	@staticmethod
	def list_comports() -> list:
		"""
		Lists all available COM-Ports
		
		Returns:
		    list: List of COM-Ports
		"""
		return serial.tools.list_ports.comports()


class Connection:

	"""
	Serial Connection
	
	Attributes:
	    baud (int): baudrate
	    filename (str): filename for saving the data
	    index (int): data index
	    port (str): COM-Port
	    t1 (float): temperature 1
	    t2 (float): temperature 2
	    t_env (float): environment temperature
	"""
	
	def __init__(self, port: str, baud: int, filename='data.csv'):
		"""Summary
		
		Args:
		    port (str): COM-Port
		    baud (int): baudrate
		    filename (str, optional): filename for saving the data
		
		Raises:
		    e: Exception if connection can't be established
		"""
		self.port = port
		self.baud = baud
		self.filename = filename
		self._terminate = False

		try:
			self._connection = serial.Serial(port, baud)

		except Exception as e:
			raise e

		self.index = deque(maxlen=20)
		self.t_env = deque(maxlen=20)
		self.t1 = deque(maxlen=20)
		self.t2 = deque(maxlen=20)

		[(self.index.append(i), self.t_env.append(20), self.t1.append(20), self.t2.append(20)) for i in range(-30, 0)]

	def send(self, data: str) -> None:
		"""
		Sends data
		
		Args:
		    data (str): Commands that will be sent
		"""
		try:
			self._connection.write(data.encode())

		except Exception as e:
			print('Unable to send data.')

	def receive(self) -> None:
		"""
		Receives incomming data
		
		Returns:
		    None: None
		"""
		f = open(self.filename, 'a')
		writer = csv.writer(f, delimiter=',')

		while not self._terminate:

			try:
				data = self._connection.readline().decode('utf-8').rstrip()

			except Exception as e:
				self._terminate = True
				print('Unable to receive data. Please check connection.')

				return

			if data and data != '':
			
				if data == "0xFF":
					self._terminate = True
					f.close()

					return

				else:
					print(data)
					_, t_env, t1, t2 = data.split(';')

					index = self.index[-1] + 1

					writer.writerow([str(index), t_env, t1, t2])

					t_env = float(t_env)
					t1 = float(t1)
					t2 = float(t2)

					if t_env >= 1000:
						t_env = 20

					elif t1 >= 1000:
						t1 = 20

					elif t2 >= 1000:
						t2 = 20

					self.index.append(index)
					self.t_env.append(t_env)
					self.t1.append(t1)
					self.t2.append(t2)


	def listen(self) -> None:
		"""
		Starts Receiving
		"""
		try:
			t = threading.Thread(target=self.receive, args=())
			t.start()

		except Exception as e:
			print('Unable to receive data.')

	def close(self) -> None:
		"""
		Closes connection
		"""
		self._terminate = True
		self._connection.close()


if __name__ == '__main__':

	app = Application()
	animate = animation.FuncAnimation(app.fig, app.animate, interval=500)
	app.mainloop()
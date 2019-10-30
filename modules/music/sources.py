import discord


class TrackingVolumeTransformer(discord.PCMVolumeTransformer):
	"""Modifies a ``PCMVolumeTransformer`` to track the progress in a source."""
	def __init__(self, *args, **kwargs):
		self.progress = 0
		self.reads = 0
		super().__init__(*args, **kwargs)
	
	def read(self):
		self.reads += 1
		if self.reads % 50 is 0:
			self.progress += 1
		return super().read()
	
	# TODO: Custom volume scale (PCMVolumeTransformer has a property `volume`)


class EmptySource(discord.AudioSource):
	"""Creates a source that plays 0.02s of silence before returning EOF."""
	used = False
	
	def is_opus(self):
		return False
	
	def read(self):
		if not self.used:
			self.used = True
			return b"\x00" * 3840
		else:
			return b""

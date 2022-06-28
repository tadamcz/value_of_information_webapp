# TODO:
# 	fix minor validation errors, see email from Marina on 26 June 2022

__version__ = "0.0.1"
__version_info__ = tuple(
	[
		int(num) if num.isdigit() else num
		for num in __version__.replace("-", ".", 1).split(".")
	]
)

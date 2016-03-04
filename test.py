
def encode_to_dict(obj):
	"""Encode a data-store model to a dictionary"""
	result = {}

	for attr in dir(obj):
		if not attr.startswith("_") and not callable(getattr(obj,attr)):
			value = getattr(obj, attr)
			result[attr] = value

	return result

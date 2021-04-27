import urllib.request
from PIL import Image
from scipy.spatial import KDTree
from webcolors import (
	CSS3_HEX_TO_NAMES,
	CSS3_NAMES_TO_HEX,
	hex_to_rgb,
)
import os
try:
	from slack_bolt import App
except:
	os.system('pip3 install slack_bolt')
	from slack_bolt import App

def css(rgb_tuple):
	css3_db = CSS3_HEX_TO_NAMES
	names = []
	rgb_values = []
	for color_hex, color_name in css3_db.items():
		names.append(color_name)
		rgb_values.append(hex_to_rgb(color_hex))
	kdt_db = KDTree(rgb_values)
	distance, index = kdt_db.query(rgb_tuple)
	return names[index]
app = App(
	token=os.environ["TOKEN"],
	signing_secret=os.environ["SIGNING"]
)

def make_image(ack, say, command, body, client):
	ack()
	def respond(message):
		client.chat_postEphemeral(
			channel=body['channel_id'],
			user=body['user_id'],
			text=message.format(user = ("<@"+body['user_id']+">"))
		)
	text = body['text'].split()
	if len(text) == 1:
		url = text[0]
		width = None
	elif len(text) == 2:
		try:
			url, width = text
			width = int(width)
		except:
			respond('Sorry, that wasn\'t a valid width!')
			return
	try:
		file = urllib.request.urlopen(url)
	except:
		respond('Sorry, that wasn\'t a valid URL!')
		return
	respond(":loading:")
	o = Image.open(file).convert('RGB')
	if width is None:
		width = 20
	h = round(o.height * (width/o.width))
	i = o.resize((width, h), resample=Image.BILINEAR)
	i.save('small.png')
	# i = i.resize((200,200), Image.NEAREST)
	out = ""
	newpixels = []
	for c, p in enumerate(i.getdata()):
		if c % width == 0 and c != 0:
			out += "\n"
		name = css(p)
		out += f":p_{name}:"
		newpixels.append(hex_to_rgb(CSS3_NAMES_TO_HEX[name]))
	new = Image.new('RGB', i.size)
	new.putdata(newpixels)
	new.save('slack.png')
	out = out.replace(':black:', ':blank:')
	with open('out', 'w+') as f:
		f.write(out)
	say(out)
	say(f"requested by <@{body['user_id']}>")

@app.command("/art")
def command(ack, say, command, body, client):
	make_image(ack, say, command, body, client)


if __name__ == "__main__":
		app.start(port=int(os.environ.get("PORT", 3000)))
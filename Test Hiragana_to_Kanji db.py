import sqlite3
import ui

conn = sqlite3.connect("HiraganaToKanji.db",check_same_thread=False)
cursor = conn.cursor()

v = ui.View()
v.frame = (0,0,400,400)
v.name = 'Test Hiragana_to_Kanji.db'

class MyTextFieldDelegate ():
	def textfield_should_return(textfield):
		cursor.execute(
			'select hiragana, kanji from Hiragana_to_Kanji where hiragana = ?',
			(textfield.text, ))
		t = ''
		for row in cursor:
			t = t + row[1] + '\n'
		textfield.superview['tv'].text = t
		textfield.end_editing()
		return True

tf = ui.TextField()
tf.frame = (10,10,380,32)
tf.delegate = MyTextFieldDelegate
v.add_subview(tf)

tv =ui.TextView(name='tv')
tv.frame = (10,50,380,340)
tv.background_color = 'white'
tv.editable = False
v.add_subview(tv)

v.present('sheet')
v.wait_modal()
conn.close()

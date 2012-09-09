An Email Module.
You can send email.command line or import it

the desc of options:

CMD:
./sendEmail.py -f "fromSomeOne@XXX.com" \
               -t "toA@XXX.com,toB@XXX.com" \
               -s "the subject of mail" \
               -m "the mail Message.Main Content" \
               -a "attachment1_path,attachment2_path"

IMPORT:
import sendEmail
sendEmail.send_mail(mail_from, mail_to, subject, msg_txt, files)
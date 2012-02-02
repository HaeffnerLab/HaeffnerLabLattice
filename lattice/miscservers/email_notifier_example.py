from email.utils import COMMASPACE

import email_notifier as em
email = em.notifier()
receps = ['haeffnerlab@gmail.com','micramm@gmail.com']
email.set_recepients(receps)
email.set_content('message','body')
email.send()
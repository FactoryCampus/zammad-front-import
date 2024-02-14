from zammad_py import ZammadAPI
import csv
import os
import magic
import base64

group = input("Zammad Group name (must be equal to Front Inbox Name): ")
client = ZammadAPI(url='https://' + input("Your Zammad Domain: ") + '/api/v1', http_token=input("Your Zammad Token: "))
existingUsers = []

def readConversation(convId, isClosed):
    articlesFile =  open('inboxes/' + group + '/' + convId + '/messages.csv', newline='')
    articles = csv.reader(articlesFile, delimiter=',', quotechar='"')
    articles.__next__()
    articlesList = reversed(list(articles))
    first = articlesList.__next__()
    ticket = createTicket(first[7], first[8], first[9], first[10], first[11], isClosed, convId, first[1])
    for article in articlesList:
        if article[4] != 'email':
            print("Error: Can only import email")
            continue
        createArticle(ticket, article[7], article[8], article[9], article[10], article[11], convId, article[1])
        
def ensureUserExists(email):
    if ", " in email:
        for mail in email.split(", "):
            ensureUserExists(mail)
        return
    if email in existingUsers:
        return
    usersearch = client.user.search(email)
    if len(usersearch) == 0:
        user = {
            'email': email,
            'roles': ['Customer']
        }
        client.user.create(params=user)
    existingUsers.append(email)

def createTicket(email, to, title, message, date, isClosed, convId, msgId):
    ensureUserExists(email)
    ensureUserExists(to)
    params = {
        "title": title,
        "group": group,
        "customer": email,
        "article": {
            "subject": title,
            "body": "empty" if message == "" else message.replace("\n","<br>"),
            "type": "email",
            "from": email,
            "to": to,
            "created_by": email,
            "origin_by": email,
            "created_at": date,
            "internal": False,
            "content_type": "text/html",
            "attachments": getAttachments(convId, msgId)
        },
        "state_id": 4 if isClosed else 1,
    }
    new_ticket = client.ticket.create(params=params)
    return new_ticket

def getAttachments(convId, msgId):
    attachments = []
    if not os.path.isdir('inboxes/' + group + '/' + convId + '/messages/' + msgId + '/'):
        return []
    for file in os.listdir('inboxes/' + group + '/' + convId + '/messages/' + msgId + '/'):
        filename = os.fsdecode(file)
        filetype = magic.from_file('inboxes/' + group + '/' + convId + '/messages/' + msgId + '/' + filename, mime=True)
        with open('inboxes/' + group + '/' + convId + '/messages/' + msgId + '/' + filename, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            attachments.append({
                "filename": filename,
                "mime-type": filetype,
                "data": encoded_string
            })
    return attachments

def createArticle(ticket, email, to, title, message, date, convId, msgId):
    ensureUserExists(to)
    ensureUserExists(email)
    params = {
        "ticket_id": ticket['id'],
        "subject": title,
        "body": "empty" if message == "" else message.replace("\n","<br>"),
        "origin_by": email,
        "type": "email",
        "from": email,
        "to": to,
        "created_by": email,
        "created_at": date,
        "internal": False,
        "content_type": "text/html",
        "attachments": getAttachments(convId, msgId)
    }
    client.ticket_article.create(params)

conversationsFile =  open('inboxes/' + group + '/conversations.csv', newline='')
conversations = csv.reader(conversationsFile, delimiter=',', quotechar='"')
conversations.__next__()
for conversation in conversations:
    print(conversation, end="")
    if conversation[2] != 'email':
        print(".. skipping because not email")
        continue
    if conversation[3] == 'trashed':
        print(".. skipping because trashed")
        continue
    readConversation(conversation[1], False if conversation[3] == 'open' else True)
    print()
    #input("Next?")



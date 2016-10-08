import socket
from select import select
import re


class bot:
    def __init__(self, host, port, nick, ident, channel):
        self.host = host
        self.port = port
        self.nick = nick
        self.ident = ident
        self.channel = channel

        self.recvbuf = []
        self.commands = {}

        self.sock = None

    def __del__(self):
        self.sendmsg("QUIT :Shutting down")
        self.sock.close()

    def sendmsg(self, msg):
        rlist, wlist, xlist = select([self.sock], [self.sock], [], 1)
        if self.sock in wlist:
            self.sock.send(str.encode("%s\r\n" % msg))

        if self.sock in rlist:
            self.recvsock()

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

        self.sendmsg("NICK %s" % self.nick)
        self.sendmsg("USER %s 0 * : Bot McBotface" % self.nick)
        self.sendmsg("JOIN %s" % self.channel)

        self.registercommand("help", self.help)

    def tick(self):
        self.recvsock()

    def recvselect(self, timeout):
        return select([self.sock], [], [], timeout)

    def recvsock(self, identSpecialCase=False):
        out = b""
        contrecv = bool(self.recvselect(0)[0])
        while (contrecv):
            buf = self.sock.recv(4096)
            if (len(buf) == 0):
                self.valid = False
            if (len(buf) < 4096 and not self.recvselect(0)[0]):  # check if there's more to receive
                contrecv = False
            out += buf


        try:
            if not identSpecialCase:
                if out:
                    self.parse(bytes.decode(out))
            else:
                return bytes.decode(out)
        except UnicodeDecodeError:
            print("Error while decoding message as unicode... shouldn't happen *shrug*")

    def parse(self, msg):
        msg = msg.splitlines()
        self.recvbuf += msg

        dellist = []
        for i in range(len(self.recvbuf)):
            if self.recvbuf[i].startswith("PING"):
                self.sendmsg(self.recvbuf[i].replace("PING", "PONG", 1))
                dellist.append(i)
            else:
                self.messageparse(self.recvbuf[i])
                dellist.append(i)

        for i in sorted(dellist, reverse=True):
            del self.recvbuf[i]

    def messageparse(self, command):
        match = re.search(":(?P<nick>.*?)!.*?PRIVMSG (?P<channel>#.*?) :!(?P<command>[^\s]*) ?(?P<args>.*)", command)

        if match:
            try:
                self.commands[match.group("command")](match.group("command"),
                                                      match.group("nick"),
                                                      match.group("channel"),
                                                      match.group("args"),
                                                      self)
            except KeyError:
                pass


    def registercommand(self, command, callback):
        self.commands[command] = callback

    def help(self, command, nick, channel, args, irc):
        self.sendmsg("NOTICE %s :Welcome to #hackvana!" % nick)
        printCommands = ""
        for availableCommand in self.commands:
            if not printCommands:
                printCommands = availableCommand
            else:
                printCommands += ", %s" % availableCommand
        self.sendmsg("NOTICE %s :This bot has the following commands available:" % nick)
        self.sendmsg("NOTICE %s :%s" % (nick, printCommands))

    def checkIfIdent(self, nick):
        self.sendmsg("PRIVMSG NickServ :ACC %s" % nick)

        identReceived = False

        buf = ""

        while(not identReceived):
            buf += self.recvsock(identSpecialCase=True)
            msgs = buf.splitlines()

            for msg in msgs:
                match = re.search(":NickServ!NickServ@services\. NOTICE %s :%s ACC (?P<mode>\d)"
                                  % (re.escape(self.nick), re.escape(nick)), msg)
                if match:
                    mode = match.group("mode")
                    if mode == "3":
                        return True
                    else:
                        return False

        self.parse(buf)











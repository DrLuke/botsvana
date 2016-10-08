import json
import time

class interests():
    def __init__(self, path):
        self.interestsPath = path
        with open(self.interestsPath, "r") as f:
            self.interests = json.loads(f.read())

    def add(self, command, nick, channel, args, irc):
        if not irc.checkIfIdent(nick):
            irc.sendmsg(
                "PRIVMSG %s :I can't let you do that %s. Please Identify with NickServ!" % (nick, nick))
            return


        if len(args) == 0:
            irc.sendmsg("NOTICE %s :Add yourself to an interest. You will be pinged whenever someone requests assistance on an interest you're subscribed to. (use !list to list those)" % nick)
            irc.sendmsg("NOTICE %s :Usage: '!add <interest1> [<interest2> ... <interestN>]'" % nick)
            return

        args = args.split(" ")

        for arg in args:
            if arg: # If not empty string
                try:
                    self.interests[arg]["users"]
                except KeyError:
                    self.interests[arg] = {}
                    self.interests[arg]["lastcalled"] = 0
                    self.interests[arg]["users"] = []
                if not nick in self.interests[arg]["users"]:
                    self.interests[arg]["users"].append(nick)

        self.saveInterests()

    def list(self, command, nick, channel, args, irc):
        if not irc.checkIfIdent(nick):
            irc.sendmsg("NOTICE %s :I can't let you do that %s. Please Identify with NickServ!" % (nick, nick))
            return

        if len(args) == 0:  #Print users interests
            interests = ""
            for key in self.interests:
                if nick in self.interests[key]["users"]:
                    if interests == "":
                        interests = key
                    else:
                        interests += ", " + key
            if not interests:
                interests = "[NONE (yet?)]"
            irc.sendmsg("NOTICE %s :Your interests: %s" % (nick, interests))
            irc.sendmsg("NOTICE %s :To see a list of existing interests, write '!list all'" % nick)
            return

        args = args.split(" ")

        if args[0] == "all":    # Print all existing interests and amount of people subscribed
            interests = ""
            for key in self.interests:
                if not interests:
                    interests = "%s [%d]" % (key, len(self.interests[key]["users"]))
                else:
                    interests += ", %s [%d]" % (key, len(self.interests[key]["users"]))

            irc.sendmsg("NOTICE %s :Existing interests: %s" % (nick, interests))

    def batsignal(self, command, nick, channel, args, irc):
        if not irc.checkIfIdent(nick):
            irc.sendmsg("NOTICE %s :I can't let you do that %s. Please Identify with NickServ!" % (nick, nick))
            return

        if len(args) == 0:
            irc.sendmsg("NOTICE %s :Summon people interested in a topic." % nick)
            irc.sendmsg("NOTICE %s :Usage: '!batsignal <topic>'" % nick)
            irc.sendmsg("NOTICE %s :To get a list of available topics, use '!list all'" % nick)

        elif args in self.interests:
            timeout = 10  # How often a batsignal can be lit

            if self.interests[args]["lastcalled"] < time.time() - timeout:
                self.interests[args]["lastcalled"] = time.time()
                self.saveInterests()
                irc.sendmsg("NOTICE %s :Summoning all subscribers of topic %s" % (nick, args))
                for user in self.interests[args]["users"]:
                    if not user == nick:
                        irc.sendmsg("NOTICE %s :%s: You have been summoned by %s because you're subsribed to topic '%s'. To unsubscribe, write '!remove %s' or '!removeall' to get removed from all topics." % (user, user, nick, args, args))
            else:
                irc.sendmsg("NOTICE %s :Too soon. Try again in %d seconds." % (nick, round(timeout - (time.time() - self.interests[args]["lastcalled"])) ))


    def remove(self, command, nick, channel, args, irc):
        if not irc.checkIfIdent(nick):
            irc.sendmsg("NOTICE %s :I can't let you do that %s. Please Identify with NickServ!" % (nick, nick))
            return

        if len(args) == 0:
            irc.sendmsg("NOTICE %s :Remove yourself from an interest." % nick)
            irc.sendmsg("NOTICE %s :Usage: '!add <interest1> [<interest2> ... <interestN>]'" % nick)
            return

        args = args.split(" ")
        removedFrom = ""
        for arg in args:
            try:
                self.interests[arg]["users"].remove(nick)
                if not removedFrom:
                    removedFrom = arg
                else:
                    removedFrom += ", %s" % arg
                if len(self.interests[arg]["users"]) == 0:
                    del self.interests[arg]
            except:
                pass

        irc.sendmsg("NOTICE %s :You have been removed from the following interests:" % nick)
        irc.sendmsg("NOTICE %s :%s" % (nick, removedFrom))

        self.saveInterests()

    def removeAll(self, command, nick, channel, args, irc):
        if not irc.checkIfIdent(nick):
            irc.sendmsg("NOTICE %s :I can't let you do that %s. Please Identify with NickServ!" % (nick, nick))
            return

        if len(args) == 0:
            irc.sendmsg("NOTICE %s :Do you really want to be removed from all interests? If yes: '!removeall yeah sure'" % nick)

        elif args == "yeah sure":
            allInterests = ""
            for key in self.interests:
                if not allInterests:
                    allInterests = key
                else:
                    allInterests += " %s" % key
            self.remove("", nick, "", allInterests, irc)

    def saveInterests(self):
        with open(self.interestsPath, "w") as f:
            f.write(json.dumps(self.interests))

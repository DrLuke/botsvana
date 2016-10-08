import irc

from interests import interests



def main():
    bot = irc.bot("chat.freenode.net", 6667, "botsvana", "", "#hackvana-dev")

    int = interests("test.json")
    bot.registercommand("add", int.add)
    bot.registercommand("list", int.list)
    bot.registercommand("batsignal", int.batsignal)
    bot.registercommand("remove", int.remove)
    bot.registercommand("removeall", int.removeAll)


    bot.connect()

    while(1):
        bot.tick()

if __name__ == "__main__":
    main()
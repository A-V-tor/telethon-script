from src import app, main, client


if __name__ == '__main__':
    client.loop.run_until_complete(main())

___HELP___
This is the help page for THE_SERVER: a server dedicated for
training & managing neural networks using NEAT algorithem.

List of commands:

_General_:

    say [args]:
        Send a message to a client which it prints to stout.

    client:
        Replies with a nice message ;)

    sound:
        Plays a pleasant sound on the client side.

    help:
        Prints this help page.

    switch [client_id]:
        switches the destination of the command to the client with the given id.

_Game_:

    get [x] [y]:
        Returns a NxN block of cell values around the given cell. Default N=5. The value is an integer representing the number of
        mines around that cell.
        -1 The cell is a mine.
        -2 The cell is not yet revealed.
        -3 The cell is flagged.
        -4 Filler for where there is no cell.

    reveal [x] [y]:
        Simulates a left click on the given coordinate.

    flag [x] [y]:
        Simulates a right click on the given coordinates.

    reset:
        Simulates pressing on the reset button.

    shutdown [option]:
        Terminates the server.
        options:

            -a
                Also Terminates all active clients.
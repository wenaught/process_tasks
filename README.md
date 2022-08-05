## Client and server for task processing
This repository contains TCP-based client and server code for task processing.

### Details
* **Task** is a unit of work, simulating a computation,
  that is run on the server. There are three types of **tasks**:
  1. Flip a string (`flip -> pilf`) with two seconds delay.
  2. Swap even and odd characters in a string (`swap -> wspa, odd -> dod`)
     with five seconds delay.
  3. Repeat each character in a string according to its position
     (`repeat -> reepppeeeeaaaaatttttt`) with seven seconds delay.

* **Server** does the following:
  1. Receives a **task** from the **client**.
  2. Adds the **task** to a queue to process one at a time.
  3. Responds to the **client** with an identifier of the **task**.
  4. 
     1. Responds with **task** status (enqueued, processing, or done).
     2. Responds with a **task** result.

* **Client** does the following:
  1. Sends **task** type and data to the **server**.
  2. 
     1. Queries the **server** for **task** status.
     2. Queries the **server** for **task** result.
  3. Works in a packet mode, which can be interrupted:
     1. Sends **task** type and data to the **server**, displays identifier.
     2. Waits for **task** result (can display status).
     3. Displays **task** result.
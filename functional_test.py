# Functional test for TOM version 201601
if __name__ == '__main__':
# Step 0: Start the server - separately started by server.py because of serve_forever()

# Step 1: Prepare 20 sets - to be separated more realistic data in future
    import random
    train_list = []
    num_count = 6000
    for n in range(1,21):
        train = (str(num_count+n) + 'S', random.choice(range(2,4)))
        train_list.append(train)

# Step 2: Start 20 clients
    import train
    import multiprocessing as mp

    for entry in train_list:
        p = mp.Process(target=train.train_client, args=(entry, 'localhost', 9877))
        p.start()

# Step 3: Each client sends approval to the server then receives approval


# Step 4: Start running and send status every 1 second


# Step 5: Display the latest status in the server


# Step 6: Once a set finished, start a new process from the list


# Step 7: Close the server when all sets had been processed


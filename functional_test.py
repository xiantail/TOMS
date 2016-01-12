# Functional test for TOM version 201601
if __name__ == '__main__':
# Step 1: Start the server


# Step 1.5: Prepare 20 sets
    import random
    train_list = []
    num_count = 6000
    for n in range(1,21):
        train = (str(num_count+n) + 'S', random.choice(range(2,4)))
        train_list.append(train)

# Step 2: Start 10 clients
    import train
    import multiprocessing as mp

    for entry in train_list:
        p = mp.Process(target=train.train_client, args=(entry,))
        p.start()

# Step 3: Each client sends approval to the server then receives approval


# Step 4: Start running and send status every 1 second


# Step 5: Display the latest status in the server


# Step 6: Once a set finished, start a new process from the list


# Step 7: Close the server when all sets had been processed


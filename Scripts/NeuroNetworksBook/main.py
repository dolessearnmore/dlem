from template import *

if not mt5.initialize(login=int(ACCOUNT), server=SERVER,password=PASSWORD):
    print("initialize() failed, error code =",mt5.last_error())
    quit()
mt5.shutdown()
# Requesting a sandbox path
path=os.path.join(mt5.terminal_info().data_path,r'MQL5\Files')
current_dir = os.getcwd()
print(current_dir)
filename = os.path.join(current_dir, "XAUUSDm_1min_data.csv")
print(pd.read_csv(filename))
print(pd.read_table(filename))

# Read the CSV file
df = pd.read_csv(filename, header=None, skipinitialspace=True, encoding='utf-8', float_precision='high')
df = df.iloc[1:]
#df.iloc[:, 2:] = df.iloc[:, 2:].apply(pd.to_numeric)
# Select numerical columns and convert to a NumPy array
data = df.iloc[:, 2:].to_numpy(dtype=np.float64)
inputs=data.shape[1]-2
targerts=2
train_data=data[:,0:inputs]
train_target=data[:,inputs:]
model = keras.Sequential([keras.Input(shape=inputs),
# Fill the model with a description of the neural layers
])
model.compile(optimizer='Adam',
loss='mean_squared_error',
metrics=['accuracy'])
callback = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=5)
history = model.fit(train_data, train_target,
epochs=500, batch_size=1000,
callbacks=[callback],
verbose=2,
validation_split=0.2,
shuffle=True)
model.save(os.path.join(path,'model.h5'))
# Drawing model learning results
plt.plot(history.history['loss'], label='Train')
plt.plot(history.history['val_loss'], label='Validation')
plt.ylabel('$MSE$ $Loss$')
plt.xlabel('$Epochs$')
plt.title('Dynamic of Models train')
plt.legend(loc='upper right')
plt.figure()
plt.plot(history.history['accuracy'], label='Train')
plt.plot(history.history['val_accuracy'], label='Validation')
plt.ylabel('$Accuracy$')
plt.xlabel('$Epochs$')
plt.title('Dynamic of Models train')
plt.legend(loc='lower right')
print(data)
print(train_data)
print(train_target)
print(inputs)
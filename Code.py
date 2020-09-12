#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd

data = pd.read_csv('Current.csv', header=None)


# In[10]:


import numpy as np

data_arc_tan = data.iloc[:, 0:20]

data_arc_tan = np.arctan(data_arc_tan)


# In[19]:


from sklearn.linear_model import LinearRegression

model = LinearRegression()
y = data[21]
model.fit(data_arc_tan, y)

y_pred = model.predict(data_arc_tan)

import matplotlib.pyplot as plt
plt.scatter(y_pred, y)
plt.show()


# In[20]:


print(y_pred, y)


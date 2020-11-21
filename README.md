Unfortunately, due to mLab MongoDB add-on discontinued, this project is currently pending additional depolyment configuration update on both mlab, and heroku dynos to restore 100% functionality.
![image](https://github.com/botaojia/cars/blob/master/flowChart.png)

As a result, I discontinued my ownership of domain www.usedcarnearby.com which was used as the full production front-end.

All the code and algorithm are still valid, if running using a locally configured mongodb connection, python3 environment.
Illustration below is still 100% valid.

![image](https://github.com/botaojia/cars/blob/master/flowChart.png)

Users can query interesting statistics of locally on market used cars. Used car price depreciation as a function of miles, years, etc, can be seen clearly.

The design is straight forward. I implemented and deployed a web crawler on cloud9 to scraping on market used car data from http://www.carsdirect.com/. The used car data is then populated into remote mongoDB on mlab. Finally the production front end is pushed to Heroku. I use Redis as a cache to reduce  query latency of remote database. The above flow chart illustrates the details.

Concerning design and coding, I'm sure there will be much better way to achieve the same purposes. However, it is a fun learning process and I'd like to document what I've learned and share with others.

The project utilizes 3 major cloud services including online dev env service “cloud9”, mongoDB service “mlab”, and “Heroku”. These 3 cloud services all provide free dyno, free workspace, etc. The scale of this simple project nicely fit into the “free lunch plan”, so that I did not spend anything except hours of research and work during 3 weekends.

Fortunately, cloud9 had a temporary promotion which enables me to use 3 free workspaces to crawling in parallel for New York, New Jersey and California data. 

Unfortunately, Heroku free dyno does not support Redis persistence. The cache will be cleaned during their maintenance window. Regardless, I configured Redis volatile-lru Maxmemory policy in case the free dyno run out of memory.

# Amazon DynamoDB - The Definitive Guide

<a href="https://www.packtpub.com/en-in/product/amazon-dynamodb-the-definitive-guide-9781803246895?type=print"><img src="https://content.packt.com/_/image/original/B18220/cover_image_large.jpg" alt="no-image" height="256px" align="right"></a>

This is the code repository for [Amazon DynamoDB - The Definitive Guide](https://www.packtpub.com/en-in/product/amazon-dynamodb-the-definitive-guide-9781803246895?type=print), published by Packt.

**Explore enterprise-ready, serverless NoSQL with predictable, scalable performance**

## What is this book about?
This guide helps you master DynamoDB, the serverless NoSQL database built for high performance at any scale. Authored by AWS experts, it covers core features, data modeling, and advanced topics, enabling you to build state-of-the-art applications.

This book covers the following exciting features:
* Master key-value data modeling in DynamoDB for efficiency
* Transition from RDBMSs to NoSQL with optimized strategies
* Implement read consistency and ACID transactions effectively
* Explore vertical partitioning for specific data access patterns
* Optimize data retrieval using secondary indexes in DynamoDB
* Manage capacity modes, backup strategies, and core components
* Enhance DynamoDB with caching, analytics, and global tables
* Evaluate and design your DynamoDB migration strategy

If you feel this book is for you, get your [copy](https://www.amazon.com/Amazon-DynamoDB-enterprise-ready-predictable-performance/dp/1803246898/ref=tmm_pap_swatch_0?_encoding=UTF8&dib_tag=se&dib=eyJ2IjoiMSJ9.u6R_md3yfBlv4qVm0pZCSklhq93iFH7Og49G-RwHnnA.nJPvHWTdQ_jwdaKIl0ZzI3h-iR0b46kA6DhYmCi2G3Q&qid=1724651746&sr=8-1) today!
<a href="https://www.packtpub.com/?utm_source=github&utm_medium=banner&utm_campaign=GitHubBanner"><img src="https://raw.githubusercontent.com/PacktPublishing/GitHub/master/GitHub.png" 
alt="https://www.packtpub.com/" border="5" /></a>

## Instructions and Navigations
All of the code is organized into folders. For example, Chapter02.

The code will look like the following:
```
import boto3

dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
table = dynamodb.Table('DefinitiveGuide01')
response = table.scan()
items = response['Items']

print(items)
```

**Following is what you need for this book:**
This book is for software architects designing scalable systems, developers optimizing performance with DynamoDB, and engineering managers guiding decision-making. Data engineers will learn to integrate DynamoDB into workflows, while product owners will explore its innovative capabilities. DBAs transitioning to NoSQL will find valuable insights on DynamoDB and RDBMS integration. Basic knowledge of software engineering, Python, and cloud computing is helpful. Hands-on AWS or DynamoDB experience is beneficial but not required.

## To get the most out of this book
We recommend reading AWS DynamoDB Developer Guide alongside this book to get a comprehensive
view of the specifics. Given that technology evolves, some limits or feature supports may have been
updated since the book was published. Note also that console screenshots may differ from the latest
version, but features and functionalities remain consistent. For the latest details, always refer to the
AWS documentation. This book complements the documentation by offering insights and best practices
drawn from more than a decade of combined DynamoDB and NoSQL experience.

While trying out the code examples can enrich your understanding, it is not mandatory. Note that
using AWS features may incur costs, typically between $2 and $5 if resources are utilized and deleted
within the same hour, with costs potentially increasing if resources remain active longer.

## Errata
**Page 191(Paragraph 1):**
<p>This also marks the end of Part 2, Core Data Modeling. The next part deals with under-the-hood information about how DynamoDB operates at the scale it does, and how it performs various functions in a distributed manner to provide blazing-fast data access and virtually unlimited scale while being highly available for its customers.</p>
<p style="font-weight: bold;"><em>Should be</em></p>
<p>With this knowledge, you are now better equipped to make informed decisions about cost optimization, scalability, and performance for your DynamoDB workloads.</p>

## Related products
* Getting Started with DuckDB [[Packt]](https://www.packtpub.com/en-in/product/getting-started-with-duckdb-9781803241005?type=print) [[Amazon]](https://www.amazon.com/Getting-Started-DuckDB-practical-efficiently/dp/1803241004/ref=sr_1_1?dib=eyJ2IjoiMSJ9.miwSyh5Ydw3YOxl8R0qRXg.0MYjqb4kUPh-t3Xa6COS1esLTuP5Ffju5MGilppuxOc&dib_tag=se&keywords=Getting+Started+with+DuckDB&qid=1724652317&sr=8-1)

* Database Design and Modeling with PostgreSQL and MySQL [[Packt]](https://www.packtpub.com/en-in/product/database-design-and-modeling-with-postgresql-and-mysql-9781803233475?type=print) [[Amazon]](https://www.amazon.com/Database-Design-Modeling-PostgreSQL-MySQL/dp/1803233478/ref=sr_1_1?crid=DPWQYWA5QFZS&dib=eyJ2IjoiMSJ9.3dy3kll2XVBj-yBgEQ3xUEI6Jtgg05VXasxeHef8qigpu2gC8RBfLV7YWrIGElHtpj0jtiolZhl67slOiIuRyXFIJjugFnZznS3fjTLavELKWNM4GLVLjoOovR0gzSPtCeoUWT6ZftUxGuxa-qpNrZ_ScMTUy5fEPKiVI6wbL7phLro2BGgp_8vtV7BrxBebUOvgru6G2Sa2FyULxk75ZYBQYtf552SR3UzHt5Ivd3U.T5xK8AqjWNbbYSWsEhJRAiF25-kX-aOMjIbv4hECsU8&dib_tag=se&keywords=Database+Design+and+Modeling+with+PostgreSQL+and+MySQL&qid=1724652418&sprefix=database+design+and+modeling+with+postgresql+and+mysql%2Caps%2C387&sr=8-1)

## Get to Know the Authors
**Aman Dhingra**
 is a Senior DynamoDB Specialist Solutions Architect at AWS, where he assists organizations in leveraging AWS to its fullest potential. He focuses on designing cost-efficient solutions and maximizing the agility and elasticity offered by the cloud and AWS. With a specialization in Amazon DynamoDB and NoSQL databases, Aman is also well-versed in AWS's big data suite of technologies, many of which are tightly integrated with open-source projects. Aman is Dublin, Ireland based.

https://www.linkedin.com/in/amdhing/ | https://x.com/amdhing  

**Mike Mackay**
 was a Senior NoSQL Specialist Solutions Architect at AWS, known as one of the early AWS Architects in Europe specializing in NoSQL technologies. Before AWS, he was Technical Director at Digital Annexe / Your Favourite Story and Head of Development for Outside Line. 

Mike's freelance work includes collaborations with Warner Brothers (UK), Heineken Music, and Alicia Keys. He has also written PHP tutorials for .net magazine and Linux Format. His projects with Outside Line featured prominent clients such as The Hoosiers, Oasis, and Paul McCartney. 

Outside work, Mike loved to chat F1 and indulge in DJ. Mike was London/Essex based. 

https://www.linkedin.com/in/mikemackay82/  | https://x.com/mikemackay  | https://www.aboutamazon.eu/news/working-at-amazon/a-second-chance-at-life 


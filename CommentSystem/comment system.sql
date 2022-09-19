db design

common table expression (CTE)
https://www.geeksforgeeks.org/cte-in-sql/

how many nested level we can have ?


level 2 comment sql query

SELECT 
    post_id,
    parent.comment as level1_comment,
    child.comment as level2_comment
FROM
    Comment parent , Comment child
WHERE
    post_id = '1111' and 
    child.parent_comment_id = parent.comment_id


Level “n” comments :
Approach 1 — Repeated Self-joins :

SELECT
    post_id,
    p1.comment as level1_comment,
    p2.comment as level2_comment,
    p3.comment as level3_comment,
    p4.comment as level4_comment,
    p5.comment as level5_comment,
    p6.comment as level6_comment
FROM        
      Comment p1
LEFT JOIN   
      Comment p2 on p2.parent_comment_id = p1.comment_id 
LEFT JOIN   
      Comment p3 on p3.parent_comment_id = p2.comment_id 
LEFT JOIN   
      Comment p4 on p4.parent_comment_id = p3.comment_id  
LEFT JOIN   
      Comment p5 on p5.parent_comment_id = p4.comment_id  
LEFT JOIN   
      Comment p6 on p6.parent_comment_id = p5.comment_id
WHERE
    post_id = '1111' and



Approach 2— Recursive CTE :
this just simplifies the query syntax and data representation , it by no means reduces the complexity of the underlying query engine.

WITH RECURSIVE cte AS 
    ( SELECT 
             comment,
             comment_id AS path,
             user_id,
             post_id
      FROM
             Comment
      WHERE parent_comment_id IS NULL 
      UNION ALL
      SELECT 
         comment,
         CONCAT(parent.path,'/',child.name)comment_id AS comment_id,
         user_id,
         post_id
      FROM
         Comment parent , Comment child
      WHERE 
         child.parent_comment_id = parent.comment_id )
SELECT * FROM cte;

The data can now looks like , denormalized and flattened.
path             | comment                | user_id     | post_id
------------------------------------------------------------------
1                | I am comment 1         | ....        | 1111
1/7              | I am comment 7         | ....        | 1111
2                | I am comment 2         | ....        | 1111
2/3              | I am comment 3         | ....        | 1111
2/3/4            | I am comment 4         | ....        | 1111
2/3/4/5          | I am comment 5         | ....        | 1111
2/3/4/5/6        | I am comment 6         | ....        | 1111



Alternative Data Model — Path-style Identifiers :
What if we create a data model to store the data in Path-style Identifier? Here we remove the self reference in “comment” table (rabbit ear) and add a new column “path”
You can now query parent comments by comparing the current row’s path to a pattern formed from the path of another row. For example, to find ancestors of comment #5 , whose path is 2/3/4/5 , do this
SELECT *
FROM
   Comment AS c
WHERE (SELECT 
          path 
       FROM 
          Comment 
       WHERE 
          comment_id = 5) LIKE c.path || '%';
This matches the patterns formed from paths of ancestor 2/3/4/% , 2/3/% and 2/%



Alternative Data Model — Closure Tables (CQRS ??):
storing all paths through. the tree , not just those with a direct parent-child relationship.

parent_comment_id             | child_comment_id 
-----------------------------------------------------
1                             | 1  
1                             | 7
2                             | 2 
2                             | 3
2                             | 4
2                             | 5
2                             | 6
3                             | 3
3                             | 4
3                             | 5
3                             | 6
4                             | 4
4                             | 5
4                             | 6
5                             | 5
5                             | 6
6                             | 6

The query to retrieve all the child comments for comment #3 will be as follows:
SELECT *
FROM
   Comment AS c
JOIN parent_child_comment p ON c.comment_id = p.child_comment_id
WHERE 
   p.parent_comment_id = 3;

The query to retrieve all the parent comments for comment #6 will be as follows:
SELECT c.*
FROM
   Comment AS c
JOIN parent_child_comment p ON c.comment_id = p.child_comment_id
WHERE 
   p.child_comment_id = 6;

Closure Table is the most versatile design for modeling multilevel deep hierarchies , it requires additional table with a lot of rows , and the extra space is a tradeoff for reducing computing efficiencies

Note : The cost for other operations INSERT , UPDATE and DELETE should also be considered while creating a Data Model. Choose the one that suits your application requirement 
on the basis of the efficiencies of these operations.

https://nehajirafe.medium.com/data-modeling-designing-facebook-style-comments-with-sql-4cf9e81eb164





Regarding fetching the comments, you can query all of the entries if you need all of them. However, if you need pagination, this solution can be a good fit. 
Lets say you select ten "base" comments per page and all the nested replies of these ten comments. In such a case, the query should select ten entries with an empty path and 
all entries where the path starts with the selected base comments.

WITH base_comments AS (
    SELECT
        *
    FROM
        "Comments"
    WHERE
        path IS NULL
    LIMIT 10 -- optional
    OFFSET 0 -- optional
) (
    SELECT
        *
    FROM
        "Comments" replies
    WHERE
        replies.path ~ ANY (
            SELECT
                id
            FROM
                base_comments))
    UNION ALL
    SELECT
        *
    FROM
        base_comments;

https://www.aleksandra.codes/comments-db-model





sample api response
{
    "code": "success",
    "message": "Get comment successful",
    "status": "200",
    "data": [
        {
            "id": "236051",
            "author_name": "Jianbo",
            "author_url": "https://wx.qlogo.cn/mmopen/vi_32/Qib5jkFMntPJnT8b2nyzKicoYSuXLeyl07ia1dianxx1fWcic9hJL4UOEuIJvoWWbx7IFia3olUGqiabZvTe0dmeFBicHQ/132",
            "date": "6 Hours ago",
            "content": "tt",
            "userid": "24",
            "child": []
        },
        {
            "id": "236028",
            "author_name": "Set sail",
            "author_url": "https://wx.qlogo.cn/mmopen/vi_32/7Aq39lKL2jxoWSMgbiaYkQzOR0mOMTm2TLjVhRicYaFXAzg20I8gpcqySYYYQMWG60p8r5kibG3ibiav3CC8Bzibjblw/132",
            "date": "2019-04-11",
            "content": "It's very simple and touching",
            "formId": null,
            "userid": "9676",
            "child": [
                {
                    "id": "236032",
                    "author_name": "Jianbo",
                    "author_url": "https://wx.qlogo.cn/mmopen/vi_32/Qib5jkFMntPJnT8b2nyzKicoYSuXLeyl07ia1dianxx1fWcic9hJL4UOEuIJvoWWbx7IFia3olUGqiabZvTe0dmeFBicHQ/132",
                    "date": "2 Days ago",
                    "content": ":-)",
                    "userid": "24",
                    "child": [
                        {
                            "id": "236040",
                            "author_name": "God loves me",
                            "author_url": "https://wx.qlogo.cn/mmopen/vi_32/QTU6iasloiaun5OX6ZcZB964vhHLAc5RuIf8kMR3nwIXvy0HibYOe9RJ9o8escDOIj7MB1vica5ibZ2XSDXIibfQMsJA/132",
                            "date": "1 Days ago",
                            "content": "Why do people choose euthanasia? Can't life be more painful than pain",
                            "userid": "9663",
                            "child": [
                                {
                                    "id": "236042",
                                    "author_name": "Jianbo",
                                    "author_url": "https://wx.qlogo.cn/mmopen/vi_32/Qib5jkFMntPJnT8b2nyzKicoYSuXLeyl07ia1dianxx1fWcic9hJL4UOEuIJvoWWbx7IFia3olUGqiabZvTe0dmeFBicHQ/132",
                                    "date": "1 Days ago",
                                    "content": "If you can't live with dignity, it's hard",
                                    "child": []
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "id": "236024",
            "author_name": "Advocating adorable",
            "author_url": "../../images/gravatar.png",
            "date": "2019-04-11",
            "content": "Everyone has his unforgettable past. Yesterday, today and tomorrow, try to live every day!",
            "userid": "0",
            "child": [
                {
                    "id": "236041",
                    "author_name": "Jianbo",
                    "author_url": "https://wx.qlogo.cn/mmopen/vi_32/Qib5jkFMntPJnT8b2nyzKicoYSuXLeyl07ia1dianxx1fWcic9hJL4UOEuIJvoWWbx7IFia3olUGqiabZvTe0dmeFBicHQ/132",
                    "date": "1 Days ago",
                    "content": "It's important to have a good day"，
                    "userid": "24",
                    "child": []
                }
            ]
        },
        {
            "id": "236018",
            "author_name": "Jielinfan",
            "author_url": "https://wx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTJBXIvvpMo5nXdlk6Mxwia9chS9E8VHGEQbDmyEAx8opRibztDzmpGHpbC3lR5vh8l4fsScZWoyEWyQ/132",
            "date": "2019-04-08",
            "content": "Best wishes to brother.",
            "userid": "280",
            "child": [
                {
                    "id": "236019",
                    "author_name": "Jianbo",
                    "author_url": "https://wx.qlogo.cn/mmopen/vi_32/Qib5jkFMntPJnT8b2nyzKicoYSuXLeyl07ia1dianxx1fWcic9hJL4UOEuIJvoWWbx7IFia3olUGqiabZvTe0dmeFBicHQ/132",
                    "date": "2019-04-09",
                    "content": ":-)",
                    "userid": "24",
                    "child": []
                }
            ]
        },
        {
            "id": "236017",
            "author_name": "Augmentation net",
            "author_url": "../../images/gravatar.png",
            "date": "2019-04-08",
            "content": "Send you a piece of sea, let you sail smoothly; send you a sun, let you warm and unrestrained; send you a sincere, wish you happy and happy; send you a blessing, let you happy every day!",
            "formId": null,
            "userid": "0",
            "child": []
        },
        {
            "id": "236011",
            "author_name": "Today's news",
            "author_url": "../../images/gravatar.png",
            "date": "2019-04-07",
            "content": "Good article, I like it very much",
            "userid": "0",
            "child": [
                {
                    "id": "236052",
                    "author_name": "Jianbo",
                    "author_url": "https://wx.qlogo.cn/mmopen/vi_32/Qib5jkFMntPJnT8b2nyzKicoYSuXLeyl07ia1dianxx1fWcic9hJL4UOEuIJvoWWbx7IFia3olUGqiabZvTe0dmeFBicHQ/132",
                    "date": "6 Hours ago",
                    "content": "Thank you",
                    "userid": "24",
                    "child": []
                }
            ]
        }
    ]
}

https://programmer.group/database-design-and-implementation-of-comment-system.html




I would try using a simple relational table for main storage with a comments table on which every comment has relations to it''s author, the parent comment, etc like you do in a relational db.
On top I would store denormalized versions of threads containing the whole thread in a tree like json structure in mongo or a posgres jsonb field.
This way you combine the consistency guarantees of a relational db with the query speed of denormalized documents.

https://www.reddit.com/r/webdev/comments/e7pb4c/database_structure_for_redditlike_comment_system/




https://stackoverflow.com/questions/16470338/comment-system-rdbms-vs-nosql







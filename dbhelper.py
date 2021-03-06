__author__ = 'Miklas Njor - iAmGoldenboy - http://miklasnjor.com'
__projectname__ = 'whos_news / dbhelper.py'
__datum__ = '15/02/17'

import pymysql
import dbconfig


import datetime

class DBHelper:

    # Connect to DB
    def connect(self, database="NE_database"):
        return pymysql.connect(host="localhost",
                               user=dbconfig.db_user,
                               passwd=dbconfig.db_pass,
                               db=dbconfig.db_name)


    def insertArticleLinksToArticleQue(self, articleLinkData):
        # http://stackoverflow.com/questions/3164505/mysql-insert-record-if-not-exists-in-table?rq=1
        # INSERT INTO table_listnames (name, address, tele)
        # SELECT * FROM (SELECT 'Rupert', 'Somewhere', '022') AS tmp
        # WHERE NOT EXISTS (
        #     SELECT name FROM table_listnames WHERE name = 'Rupert'
        # ) LIMIT 1;
        connection = self.connect()

        try:
            query = """INSERT IGNORE INTO articleQue(articleLink,sektion, avis, seen )
            SELECT * FROM (SELECT '{}', '{}', '{}', {}) AS tmp
            WHERE NOT EXISTS (
                SELECT articleLink FROM articleQue WHERE articleLink = '{}'
            ) LIMIT 1;""".format(articleLinkData[0], articleLinkData[1], articleLinkData[2], 0, articleLinkData[0])

            # print(query )

            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
        except Exception as e:
            print("Insert article error with : {} // -- // due to {}".format(articleLinkData, e) )
        finally:
            connection.close()

    def seenArticle(self, articleLink):
        connection = self.connect()
        try:
            query = """UPDATE articleQue SET seen=1 WHERE articleLink='{}';""".format(articleLink)
            # print("Seen article", query)
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
        except Exception as e:
            print("Seen article error with : {} /--- due to {}".format(articleLink, e) )
        finally:
            connection.close()

    def getArticleQue(self,limit=20):
        connection = self.connect()
        try:
            query = """SELECT articleLink, avis, sektion FROM articleQue WHERE seen = 0 LIMIT {}; """.format(limit)
            # print("Get article que", query)
            with connection.cursor() as cursor:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print("article Que (LIMIT {}) error due to : {}".format( limit, e) )
        finally:
            connection.close()

    def getHTMLtags(self):
        connection = self.connect()
        try:
            query = """SELECT DISTINCT tagArea FROM html_tags; """
            # print("getHTMLtags: ", query)
            with connection.cursor() as cursor:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print("Couldn't get HTML TAGS, error due to : {}".format(  e) )
        finally:
            connection.close()

    def getHTMLtagItem(self, avis, tagArea):
        connection = self.connect()
        try:
            query = "SELECT tagData from html_tags WHERE avis='{}' and tagArea='{}';".format(avis, tagArea)
            # print("getHTMLtagItem Tag area", query)
            with connection.cursor() as cursor:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print("getHTMLtagItem tag area error: ", e)
        finally:
            connection.close()


    def deleteFromArticleQue(self,intervalNum=3, intervalType="day"):
        connection = self.connect()

        try:
            query = """DELETE FROM articleQue WHERE insertDate <= DATE_SUB(NOW(), INTERVAL {} {});""".format(intervalNum, intervalType )

            print("Del from artque", query )

            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
        except Exception as e:
            print("Couldn't delete article from: {} {} due to : {}".format(intervalNum, intervalType, e) )
        finally:
            connection.close()

    def countRecentArticles(self,startTime=1, endTime=2, startTimeType="hour", endTimeType="hour"):
        connection = self.connect()
        try:
            query = """SELECT COUNT(*), sektion, avis
                    FROM articleLinks
                    WHERE date >= DATE_SUB(NOW(), INTERVAL {} {})
                       AND date <= DATE_SUB(NOW(), INTERVAL {} {})
                    GROUP BY sektion, avis
                    ORDER BY avis, sektion;""".format( endTime, endTimeType, startTime, startTimeType)
            print("countRecentArticles : ", query)
            with connection.cursor() as cursor:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print("Count article que error due to : ", e)
        finally:
            connection.close()


    def countArticlesQue(self):
        connection = self.connect()
        try:
            query = """SELECT COUNT(*) FROM articleQue; """
            # print("countArticlesQue : ", query)
            with connection.cursor() as cursor:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print("Count article que error due to : ", e)
        finally:
            connection.close()

    def countArticlesQueSeen(self):
        connection = self.connect()
        try:
            query = """SELECT COUNT(*) FROM articleQue WHERE seen=1; """
            # print("countArticlesQueSeen : ", query)
            with connection.cursor() as cursor:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print("Count article que error due to : ", e)
        finally:
            connection.close()

    def countArticlesQueNotSeen(self):
        connection = self.connect()
        try:
            query = """SELECT COUNT(*) FROM articleQue WHERE seen=0; """
            # print("countArticlesQueNotSeen : ", query)
            with connection.cursor() as cursor:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print("Count article que error due to : ", e)
        finally:
            connection.close()


    def get_all_feeds(self):
        connection = self.connect()
        try:
            query = """SELECT avis, sektion, medietype, rssLink, lastUpdate from rss_feeds ORDER BY medietype, avis, sektion; """
            with connection.cursor() as cursor:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print("Get all feeds error due to : ", e)
        finally:
            connection.close()


    def getItemID(self,id_key, table, id_field, item, multiple=False):
        """ Gets the ID (primary key) for the item in question.
        :param id_key: i.e. 'article_id'
        :param table: i.e. <table> 'articleLinks
        :param id_field: i.e <other fields to look in> 'articlelink' or 'ne'
        :param item: i.e. 'articleLink'
        :return:
        """

        connection = self.connect()
        try:
            if multiple == False:
                query = """SELECT {} FROM {} WHERE {}='{}'; """.format(id_key, table, id_field, item)
            else:
                query = """SELECT {}, {} FROM {} WHERE {} = {} AND {} = {};""".format(id_field[0], id_field[1], table, id_field[0], item[0], id_field[1], item[1] )
            # SELECT ne_id FROM namedEntities WHERE ne='some name';

            # print("getItemID", query)
            with connection.cursor() as cursor:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print("no where :) to be found due to : ", id_key, table, id_field, item, e)
        finally:
            connection.close()



    def insertSocialMedia(self, article_id, enumValue, count):

        connection = self.connect()
        try:
            # query = """INSERT INTO articleSocialMediaCount (socialMedia_art_id, socialMediaID, socialMediaCount)
            # VALUES ({}, '{}', {});""".format(article_id, enumValue, count)
            query = """INSERT INTO articleSocialMediaCount (socialMedia_art_id, socialMediaID, socialMediaCount)
            SELECT * FROM (SELECT {}, '{}', {}) AS tmp
            WHERE NOT EXISTS (
                SELECT socialMedia_art_id, socialMediaID, socialMediaCount FROM articleSocialMediaCount WHERE socialMedia_art_id = {} AND socialMediaID = '{}' AND socialMediaCount = {}
            ) LIMIT 1;""".format(article_id, enumValue, count, article_id, enumValue, count)
            # print("insertSocialMedia -> ", query)
            with connection.cursor() as cursor:
                cursor.execute(query)
            connection.commit()
        except Exception as e:
            print("Error with {} / {} / {} : {} due to : {}".format(article_id, enumValue, count, e))
        finally:
            connection.close()

    def insertArticleSocialWatchlist(self, article_id):

        connection = self.connect()
        try:
            # query = """INSERT INTO articleSocialMediaCount (socialMedia_art_id, socialMediaID, socialMediaCount)
            # VALUES ({}, '{}', {});""".format(article_id, enumValue, count)
            query = """INSERT INTO socialWatchList (socialMedia_art_id, socialMediaID, socialMediaCount)
            SELECT * FROM (SELECT {}, '{}', {}) AS tmp
            WHERE NOT EXISTS (
                SELECT socialMedia_art_id, socialMediaID, socialMediaCount FROM articleSocialMediaCount WHERE socialMedia_art_id = {} AND socialMediaID = '{}' AND socialMediaCount = {}
            ) LIMIT 1;""".format(article_id)
            # print("insertSocialMedia -> ", query)
            with connection.cursor() as cursor:
                cursor.execute(query)
            connection.commit()
        except Exception as e:
            print("Error with {} / {} / {} : {} due to : {}".format(article_id))
        finally:
            connection.close()

    def insertValuesReturnID(self, tableName, tableFields, values, lookFor, item2look4, item_id='', mode="single", returnID=False, printQuery=False):
        """ Insert values to the database, and returns the row_id if returnID = True
        http://stackoverflow.com/questions/3164505/mysql-insert-record-if-not-exists-in-table?rq=1
        :param tableName:   Name of the table
        :param tableFields: List of fields you want to insert into
        :param values:      List of values you want to insert into the fields
        :param lookFor:     What to look for in table, typically 'ne' or 'name' type of value
        :param item2look4:  Item to look for, typically 'some ne' or 'real name' WHERE lookfor = item2look4
        :param item_id:     Used to return the id_row, i.e. 'ne_id' or 'article_id'. Default empty.
        :param returnID:    Should the function return a row_id of what that has just been updated.
        :return:            The row_id of what that has just been updated, if returnID=True
        """

        newvalues = ""
        for value in values:
            if isinstance(value, int):
                newvalues += "{},".format(value)
            elif isinstance(value, str):
                newvalues += "'{}',".format(value)
        newvalues = newvalues[:len(newvalues)-1]
        tableFields = ", ".join(tableFields)
        # print(tableFields)


        connection = self.connect()

        try:
            multiple = False
            if mode == "single":
                query = """INSERT INTO {} ({})
            SELECT * FROM (SELECT {}) AS tmp
            WHERE NOT EXISTS (
                SELECT {} FROM {} WHERE {} = '{}'
            ) LIMIT 1;""".format(tableName, tableFields, newvalues, lookFor, tableName, lookFor, item2look4)

            elif mode == "ne2art":
                # table: namedEntities2articles
                query = """INSERT IGNORE INTO {} ({}) VALUES ({});""".format(tableName, tableFields, newvalues)

            elif mode == "foaf":
                # table: foaf
                query = """INSERT INTO {} ({})
            SELECT * FROM (SELECT {}) AS tmp
            WHERE NOT EXISTS (
                SELECT {}, {} FROM {} WHERE {} = {} AND {} = {}
            ) LIMIT 1;""".format(tableName, tableFields, newvalues, lookFor[0], lookFor[1], tableName, lookFor[0], item2look4[0], lookFor[1], item2look4[1])
                multiple = True

            # print("insertValuesReturnID ----> ", query )
            if printQuery == True:
                print(query)

            with connection.cursor() as cursor:
                cursor.execute(query)
                lastID = cursor.lastrowid
            connection.commit()

            if returnID == True:
                if lastID == 0:
                    try:
                        lastID = self.getItemID(item_id, tableName, lookFor, item2look4, multiple=multiple)[0][0]
                    except Exception as e:
                        print("Couldn't get hold of id: {} for {}: {} -> due to : {}".format(item_id, tableName, item2look4, e))
                return lastID

        except UnicodeError as e:

            print("Unicode error. Trying alternative insertion. The error is with table: {} fields: {} values: {} lookfor: {} item: {} due to : {}".format(tableName, tableFields, values, lookFor, item2look4, e))

            try:
                # Yay, works! -ish :(
                query = """INSERT INTO {} ({})
            SELECT * FROM (SELECT {}) AS tmp
            WHERE NOT EXISTS (
                SELECT {} FROM {} WHERE {} = '{}'
            ) LIMIT 1;""".format(tableName, tableFields, newvalues.encode('latin-1', 'ignore').decode('latin-1'), lookFor, tableName, lookFor, item2look4.encode('latin-1', 'ignore').decode('latin-1'))

                if printQuery == True:
                    print(query)

                with connection.cursor() as cursor:
                    cursor.execute(query)
                    lastID = cursor.lastrowid
                connection.commit()

                if returnID == True:
                    if lastID == 0:
                        try:
                            lastID = self.getItemID(item_id, tableName, lookFor, item2look4.encode('latin-1', 'ignore').decode('latin-1'))[0][0]
                        except Exception as e:
                            print("Couldn't get hold of id: {} for {}: {} -> due to : {}".format(item_id, tableName, item2look4.encode('latin-1', 'ignore').decode('latin-1'), e))
                    return lastID

                print("Alternative insertion worked for orig {} -> {}".format(newvalues, newvalues.encode('latin-1', 'ignore').decode('latin-1')))

            except Exception as e:
                print("Converting to Latin-1 didn't work with table: {} fields: {} values: {} lookfor: {} item: {} due to : {}".format(tableName, tableFields, values, lookFor, item2look4, e))


        except Exception as e:
            print("Error with table: {} fields: {} values: {} lookfor: {} item: {} due to : {}".format(tableName, tableFields, values, lookFor, item2look4, e))
        finally:
            connection.close()


    def getNamedEntityExact(self,namedEntity):
        connection = self.connect()
        try:

            query = """SELECT DISTINCT ne_id, ne, neOccuranceCount AS overallCount, neOccuranceHead AS overallHeadCount, neOccuranceTail AS overallTailCount, neOccurranceShape AS shape, sektion, avis, articleLink, date, article_id
                        FROM namedEntities
                        JOIN namedEntity2Articles
                          on ne2art_ne_id=ne_id
                        JOIN articleLinks
                          on ne2art_art_id=article_id
                        WHERE ne = '{}'
                        ORDER BY ne, date, avis, sektion, overallCount;""".format(namedEntity)

            # print("getItemID", query)
            with connection.cursor() as cursor:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print("no where :) to be found due to : ", namedEntity, e)
        finally:
            connection.close()

    def getNamedEntityFuzzy(self,namedEntity):
        connection = self.connect()
        try:

            query = """SELECT DISTINCT ne_id, ne, neOccuranceCount AS overallCount, neOccuranceHead AS overallHeadCount, neOccuranceTail AS overallTailCount, neOccurranceShape AS shape, sektion, avis, articleLink, date, article_id
                        FROM namedEntities
                        JOIN namedEntity2Articles
                          on ne2art_ne_id=ne_id
                        JOIN articleLinks
                          on ne2art_art_id=article_id
                        WHERE ne LIKE '{}'
                        ORDER BY ne, date DESC, avis, sektion, overallCount;""".format(namedEntity)

            # print("getItemID", query)
            with connection.cursor() as cursor:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print("no where :) to be found due to : ", namedEntity, e)
        finally:
            connection.close()

    def getSocialMediaDataForArticleID(self,article_id):
        connection = self.connect()
        try:

            query = """SELECT DISTINCT date, socialMediaID, socialMediaCount
                        FROM articleSocialMediaCount
                        WHERE socialMedia_art_id = {}
                        ORDER BY date DESC;""".format(article_id)

            # print("getSocialMediaDataForArticleID", query)
            with connection.cursor() as cursor:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print("No getSocialMediaDataForArticleID data for {} to be found due to : {}".format(article_id, e) )
        finally:
            connection.close()

    def getArticleCountPerMedia(self):

        connection = self.connect()
        try:

            query = """ SELECT rss_feeds.avis, rss_feeds.sektion, rssLink,   count(article_id)
                    FROM rss_feeds
                    JOIN articleLinks
                      ON rss_feeds.avis=articleLinks.avis
                      AND rss_feeds.sektion=articleLinks.sektion
                    GROUP BY name
                    ORDER BY rss_feeds.avis, rss_feeds.sektion;
                 """

            with connection.cursor() as cursor:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print("No getArticleCountPerMedia data to be found - due to : {}".format( e) )
        finally:
            connection.close()

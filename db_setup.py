__author__ = 'Miklas Njor - iAmGoldenboy - http://miklasnjor.com'
__projectname__ = 'whos_news / db_setup.py'
__datum__ = '16/02/17'

import pymysql
import dbconfig

connection = pymysql.connect(host='localhost',
                             user= dbconfig.db_user,
                             passwd=dbconfig.db_pass,
                             db = dbconfig.db_name
                             )

try:
    with connection.cursor() as cursor:
        # try:
        #     sql = "CREATE DATABASE IF NOT EXISTS NE_database;"
        #     cursor.execute(sql)
        # except Exception as e:
        #     print("Cant create database due to: ", e)

        try:
            sql = """CREATE TABLE IF NOT EXISTS NE_database.rss_feeds (
rss_id INT NOT NULL AUTO_INCREMENT,
name VARCHAR(30) NOT NULL UNIQUE,
rssLink VARCHAR(450) NOT NULL UNIQUE,
avis VARCHAR(40) NOT NULL,
country VARCHAR(250) DEFAULT 'Denmark',
medietype ENUM('Dagblad', 'Ugeblad', 'TV', 'Fagblad', 'Radio') NOT NULL, /* should translate */
/* reach ENUM('Regional', 'Natiaonal', 'International') NOT NULL, */ /* Perhaps some kind of list for which regions */
sektion ENUM('Kultur', 'Indland', 'Udland', 'Sport', 'Økonomi', 'Politik', 'Debat') NOT NULL,
lastUpdate DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
PRIMARY KEY(`rss_id`, `avis`)
) ENGINE=INNODB;

/* table for former dudds - that have been split in two - because I need to curate this shit
NE's that are curated, have to be marked as such and receive less points
*/

/* table for analytics to cut down on the processing - gets updated every ten minutes */

CREATE TABLE IF NOT EXISTS NE_database.html_tags (
html_id INT NOT NULL AUTO_INCREMENT,
avis VARCHAR(40) NOT NULL,
tagData VARCHAR(450) NOT NULL,
tagArea ENUM('overskriftTag', 'underrubrikTag', 'billedtekstTag', 'introTag', 'bylineTag', 'mellemrubrikTag', 'quoteTag', 'brodtextTag') NOT NULL,
dateAdded DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
PRIMARY KEY(`html_id`)
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS NE_database.articleQue (
article_que_id INT NOT NULL AUTO_INCREMENT,
articleLink VARCHAR (450) NOT NULL UNIQUE,
avis VARCHAR(40),
sektion VARCHAR(40),
seen INT DEFAULT 0,
insertDate DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
PRIMARY KEY(`article_que_id`)
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS NE_database.articleLinks (
article_id INT NOT NULL AUTO_INCREMENT,
articleLink VARCHAR(450) NOT NULL UNIQUE,
date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
sektion VARCHAR(40) NOT NULL,
avis VARCHAR(40) NOT NULL,
PRIMARY KEY(`article_id`)
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS NE_database.articleSocialMediaCount (
sm_id INT NOT NULL AUTO_INCREMENT,
date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
socialMedia_art_id INT NOT NULL,
socialMediaID ENUM(/*'Facebook_total_count',*/'Facebook_like_count', 'Facebook_share_count', 'Facebook_comment_count', 'Twitter', 'LinkedIn', 'GooglePlusOne', 'Pinterest', 'StumbleUpon') NOT NULL,
socialMediaCount INT NOT NULL,
PRIMARY KEY(`sm_id`),
FOREIGN KEY (`socialMedia_art_id`)
    REFERENCES articleLinks(`article_id`)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS NE_database.namedEntities (
ne_id INT NOT NULL AUTO_INCREMENT,
ne VARCHAR(60) NOT NULL UNIQUE,
/* added from duddification - some kind of value or score */
addedDate DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
PRIMARY KEY(`ne_id`, `ne`)
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS NE_database.namedAliases (
alias_id INT NOT NULL AUTO_INCREMENT,
alias_ne VARCHAR(60) NOT NULL UNIQUE,
original_ne_id INT,
addedDate DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
PRIMARY KEY(`alias_id`, `alias_ne`, `original_ne_id`),
FOREIGN KEY (`original_ne_id`)
    REFERENCES namedEntities(`ne_id`)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=INNODB;


/* CREATE UNIQUE INDEX ix_ReversePK ON  Auto2AutoFeature (auto_feature_id, auto_id); */
/* http://www.joinfu.com/2005/12/managing-many-to-many-relationships-in-mysql-part-1/ */

CREATE TABLE IF NOT EXISTS NE_database.namedEntity2Articles (
ne2art_id INT NOT NULL AUTO_INCREMENT,
ne2art_ne_id INT NOT NULL,
ne2art_art_id INT NOT NULL,
neOccuranceCount INT NOT NULL,
neOccuranceHead INT,
neOccuranceTail INT,
neOccurranceShape ENUM('descending', 'ascending', 'solid', 'diamond', 'hourglass'),
addedDate DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
PRIMARY KEY(`ne2art_id`, `ne2art_ne_id`, `ne2art_art_id`) /* , */
/* UNIQUE KEY `ne2art_ne_id` (`ne2art_ne_id`,`ne2art_art_id`), */
/* FOREIGN KEY (`ne2art_ne_id`) */
/*    REFERENCES namedEntities(`ne_id`) */
/*    ON UPDATE CASCADE ON DELETE CASCADE, */
/* FOREIGN KEY (`ne2art_art_id`) */
/*    REFERENCES articleLinks(`article_id`) */
/*    ON UPDATE CASCADE ON DELETE CASCADE */
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS NE_database.foaf (
foaf_id INT NOT NULL AUTO_INCREMENT,
foaf_ne_id  INT NOT NULL,
foaf_knows_id  INT NOT NULL,
foaf_art_id INT NOT NULL,
addedDate DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
PRIMARY KEY (`foaf_id`),
FOREIGN KEY (`foaf_ne_id`)
    REFERENCES namedEntities(`ne_id`)
    ON UPDATE CASCADE ON DELETE CASCADE,
FOREIGN KEY (`foaf_art_id`)
    REFERENCES articleLinks(`article_id`)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=INNODB;


INSERT IGNORE INTO rss_feeds (name, rssLink, sektion, avis, medietype)
VALUES ('k.dk-u', 'http://www.kristeligt-dagblad.dk/rss/udland', 'Udland', 'Kristeligt Dagblad', 'Dagblad');
INSERT IGNORE INTO rss_feeds (name, rssLink, sektion, avis, medietype)
VALUES ('b-Kultur' ,'http://www.b.dk/feeds/rss/kultur' , 'Kultur' , 'Berlingske Tidende', 'Dagblad');
INSERT IGNORE INTO rss_feeds (name, rssLink, sektion, avis, medietype)
VALUES ('b-Indland','http://www.b.dk/feeds/rss/Nationalt' , 'Indland' , 'Berlingske Tidende', 'Dagblad');
INSERT IGNORE INTO rss_feeds (name, rssLink, sektion, avis, medietype)
VALUES ('b-Udland', 'http://www.b.dk/feeds/rss/Globalt' , 'Udland' , 'Berlingske Tidende', 'Dagblad');
INSERT IGNORE INTO rss_feeds (name, rssLink, sektion, avis, medietype)
VALUES ('p-Indland', 'http://politiken.dk/rss/indland.rss' , 'Indland' , 'Politiken', 'Dagblad');
INSERT IGNORE INTO rss_feeds (name, rssLink, sektion, avis, medietype)
VALUES ('p-Udland', 'http://politiken.dk/rss/udland.rss' , 'Udland' , 'Politiken', 'Dagblad');
INSERT IGNORE INTO rss_feeds (name, rssLink, sektion, avis, medietype)
VALUES ('p-Kultur', 'http://politiken.dk/rss/kultur.rss' , 'Kultur' , 'Politiken', 'Dagblad');
INSERT IGNORE INTO rss_feeds (name, rssLink, sektion, avis, medietype)
VALUES ('p-oekonomi', 'http://politiken.dk/rss/oekonomi.rss' , 'Økonomi' , 'Politiken', 'Dagblad');
INSERT IGNORE INTO rss_feeds (name, rssLink, sektion, avis, medietype)
VALUES ('j-Indland', 'http://jyllands-posten.dk/indland/?service=rssfeed' , 'Indland' , 'Jyllands-Posten', 'Dagblad');
INSERT IGNORE INTO rss_feeds (name, rssLink, sektion, avis, medietype)
VALUES ('j-Udland', 'http://jyllands-posten.dk/international/?service=rssfeed', 'Udland' , 'Jyllands-Posten', 'Dagblad');
INSERT IGNORE INTO rss_feeds (name, rssLink, sektion, avis, medietype)
VALUES ('j-Kultur', 'http://jyllands-posten.dk/kultur/?service=rssfeed' , 'Kultur' , 'Jyllands-Posten', 'Dagblad');
INSERT IGNORE INTO rss_feeds (name, rssLink, sektion, avis, medietype)
VALUES ('j-politik', 'http://jyllands-posten.dk/politik/?service=rssfeed' , 'Politik' , 'Jyllands-Posten', 'Dagblad');
INSERT IGNORE INTO rss_feeds (name, rssLink, sektion, avis, medietype)
VALUES ('eb-Indland', 'http://ekstrabladet.dk/rss2/?mode=normal&submode=nyheder' , 'Indland' , 'Ekstra Bladet', 'Dagblad');
INSERT IGNORE INTO rss_feeds (name, rssLink, sektion, avis, medietype)
VALUES ('eb-Kultur', 'http://ekstrabladet.dk/rss2/?mode=normal&submode=flash' , 'Kultur' , 'Ekstra Bladet', 'Dagblad');
INSERT IGNORE INTO rss_feeds (name, rssLink, sektion, avis, medietype)
VALUES ('bt-Indland', 'http://www.bt.dk/nyheder/seneste/rss' , 'Indland' , 'BT', 'Dagblad');
INSERT IGNORE INTO rss_feeds (name, rssLink, sektion, avis, medietype)
VALUES ('bt-Kultur', 'http://www.bt.dk/underholdning/seneste/rss' , 'Kultur' , 'BT', 'Dagblad');
INSERT IGNORE INTO rss_feeds (name, rssLink, sektion, avis, medietype)
VALUES ('k.dk-i', 'http://www.kristeligt-dagblad.dk/rss/danmark', 'Indland', 'Kristeligt Dagblad', 'Dagblad');
INSERT IGNORE INTO rss_feeds (name, rssLink, sektion, avis, medietype)
VALUES ('k.dk-k', 'http://www.kristeligt-dagblad.dk/rss/kultur', 'Kultur', 'Kristeligt Dagblad', 'Dagblad');
INSERT IGNORE INTO rss_feeds (name, rssLink, sektion, avis, medietype)
VALUES ('information-i', 'https://www.information.dk/feed', 'Indland', 'Information', 'Dagblad');



INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('Politiken', '.article__title', 'overskriftTag' );
INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('Politiken', '.article__summary', 'underrubrikTag' );
INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('Politiken', '.media__image', 'billedtekstTag' );
INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('Politiken', '.body__h3', 'mellemrubrikTag' );
INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('Politiken', '.quote__p', 'quoteTag' );
INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('Politiken', '.body__p', 'brodtextTag' );


INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('Jyllands-Posten', 'h1', 'overskriftTag' );
INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('Jyllands-Posten', '.artDescription p', 'billedtekstTag' );
INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('Jyllands-Posten', '.artImgCaption', 'billedtekstTag' );
INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('Jyllands-Posten', '.articleText h3', 'mellemrubrikTag' );
INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('Jyllands-Posten', '#articleText p', 'brodtextTag' );

INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('Berlingske Tidende', '.article-header__title', 'overskriftTag' );
INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('Berlingske Tidende', '.article-header__summary', 'underrubrikTag' );
INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('Berlingske Tidende', '.article-content__image-caption', 'billedtekstTag' );
INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('Berlingske Tidende', '.article-body p', 'brodtextTag' );

INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('BT', '.article-title', 'overskriftTag' );
INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('BT', '.image-caption', 'billedtekstTag' );
INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('BT', '.article-content p', 'brodtextTag' );


INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('Ekstra Bladet', '.rubrik', 'overskriftTag' );
INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('Ekstra Bladet', '.underrubrik', 'underrubrikTag' );
INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('Ekstra Bladet', '.mediacontrols .text', 'billedtekstTag' );
INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('Ekstra Bladet', '.bodytext p', 'brodtextTag' );

INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('Information', '.title-not-premium', 'overskriftTag' );
INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('Information', '.field-name-field-underrubrik', 'underrubrikTag' );
INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('Information', '.field-name-field-description p', 'billedtekstTag' );
INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('Information', '.field-name-body h4', 'mellemrubrikTag' );
INSERT INTO html_tags (avis, tagData, tagArea)
VALUES ('Information', '.field-name-body p', 'brodtextTag' );

INSERT INTO html_tags (avis, tagData, tagArea)
    VALUES ('Kristeligt Dagblad', '.node-title', 'overskriftTag' );
INSERT INTO html_tags (avis, tagData, tagArea)
    VALUES ('Kristeligt Dagblad', '.field-name-field-underrubrik', 'underrubrikTag' );
INSERT INTO html_tags (avis, tagData, tagArea)
    VALUES ('Kristeligt Dagblad', '.slide-comments .caption', 'billedtekstTag' );
INSERT INTO html_tags (avis, tagData, tagArea)
    VALUES ('Kristeligt Dagblad', '.content .field p', 'brodtextTag' );
INSERT INTO html_tags (avis, tagData, tagArea)
    VALUES ('Kristeligt Dagblad', '.post-author-name a', 'bylineTag' );
INSERT INTO html_tags (avis, tagData, tagArea)
    VALUES ('Kristeligt Dagblad', '.content p', 'introTag' );

"""
            cursor.execute(sql)
        except Exception as e:
            print(e)

    connection.commit()
except Exception as e:
    print("fuck - no database created.... :( ", e)
finally:
    connection.close()

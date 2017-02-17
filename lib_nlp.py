__author__ = 'Miklas Njor - iAmGoldenboy - http://miklasnjor.com'
__projectname__ = 'whos_news / lib_nlp.py'
__datum__ = '16/02/17'

from nltk.tokenize import sent_tokenize
from nltk.stem import SnowballStemmer, snowball
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk import tree, trigrams, word_tokenize, pos_tag, ne_chunk, ne_chunk_sents
from collections import Counter
import string
from fuzzywuzzy import fuzz
import numpy as np
import time

import nltk
from nltk.collocations import *

from dbconfig import setNLTKdataLink

if len(setNLTKdataLink()) > 0:
    #  http://stackoverflow.com/questions/13965823/resource-corpora-wordnet-not-found-on-heroku/37558445#37558445
    who = setNLTKdataLink()
    # print("who", who)
    nltk.data.path.append(str(who))


udvidestopwords = ["ham", "derfor", "seks", "begge", "dermed", "reuters", "hvornår", "inden", "hele", "selvom", "læserbrev", "mon", "kom", "tag", "ingen", "herunder", "især", "sagen", "allerede", "sidste", "første", "selvfølgelig", "heldigvis", "hver", "arkivfotoFoto", "arkivfoto", "kan", "endnu", "modtag e-mail", "anmeldelse", "måske", "følg", "dengang", "live", "berlingske", "anmeldelse", "ja", "nej", "ritzau", "reuters" "kun", "læs", "foto", "siger", "sagde", "mente", "mens", "både", "desuden", "eksperter", "ifølge", "føler", "følte", "flere", "mange", "udover", "samlet", "mener", "fortæller", "håber", "så", "altså", "hvem", "hvad", "hvor", "hvorfor", "hvordan", "hvilket", "hvilken", "tror", "troede", 'tekst', 'cccfoto', 'afp', 'politiken', 'send', 'journalist', 'offer', 'mest', 'drop', 'fyren', 'gode', 'selvmål', 'tvertimod', 'tværtimod', 'først', 'skrev', 'hverken', 'ligesom', 'blinkFoto', 'bagud', 'aldrig', 'samtidig', 'beslutningen', 'siden', 'alligevel', 'tak', 'nemlig', 'film', 'planen', 'samtidig', 'igennem', 'dér', 'fordi', 'pludselig', 'stejlt', 'enten', 'indtast', 'tilbuddet', 'må', 'måtte', 'skuespiller', 'forsøger', 'syg', 'halvsløje', 'testen', 'ved', 'sidst', 'lige', 'titlen', 'udsolgt', 'faldet', 'imidlertid', 'overblik', 'allerhelst', 'ændringen', 'årsagen', 'efterfølgende', 'udsat', 'tilbudet', 'uden', 'historien', 'herfra', 'ansvaret', 'næste', 'forestil', 'dagen', 'fjerde', 'uanset', 'endelig', 'netop', 'minderne', 'næste', 'ideen', 'idéen', 'kendsgerningerne', 'tankerne', 'foreløbig', 'lige', 'overfor', 'uden', 'uheldet', 'heldet', 'lugten', 'turen', 'moderne', 'tiltrængte', 'intet', 'oplevelsen', 'svaret', 'debat', 'synd', 'moderne', 'selvet', 'senest', 'børn', 'pligten', 'ansvaret', 'helst', 'pludseligt', 'stilhed', 'små', 'historien', 'desværre', 'håbløshed', 'forestillingen', 'håbløsheden', 'således', 'brug', 'slået', 'ejeren', 'farlig', 'sidstnævnte', 'parret', 'derefter', 'imidlertid', 'forleden', 'mere', 'voksende', 'ulovlig', 'familie', 'sammenlignet', 'forskellen', 'gør', 'absolut', 'bestemt', 'dernæst', 'dertil', 'præcis', 'satser', 'mulig', 'blandt', 'gruppen', 'se', 'ekstra', 'usædvanlig', 'faktisk', 'udnævne', 'arkiv', 'svaret', 'problemet', 'iført', 'søger', 'stoffet', 'undersøgelse', 'lækkede', 'tilsyneladende']
dk_Stopwords = stopwords.words('danish') + udvidestopwords
dk_tokenizer = nltk.data.load("tokenizers/punkt/danish.pickle")
dk_Stemmer = SnowballStemmer('danish')


bigram_measures = nltk.collocations.BigramAssocMeasures()
trigram_measures = nltk.collocations.TrigramAssocMeasures()


def scrubString(string):
    """ Removes bad chars from the string
    :param string: the string to be scrubbed to remove bad chars
    :return: the scrubbed string
    """

    try:
        cleanString = string.strip().replace("  ", " ").replace("»", " ").replace("’"," ").replace("”", " , ").replace(":", " . ").replace("«", " ").replace("\n", " ").replace('"', " ").replace("'", " ")

        return cleanString
    except Exception as e:
        print("Couldn't scrub string due to : ", e)



def removeStopwordsFromString(sentenceList):
    """
    :param sentenceList: sentence string
    :return: sentence string with no stopwords.
    """

    finalOutput = []
    sentencesChunks = False

    try:
        contents = scrubString(sentenceList)
        sentencesChunks = dk_tokenizer.tokenize(contents)
    except Exception as e:
        print("removeStopwordsFromString error: Could not scrub or chunk sentences due to : ", e)

    if sentencesChunks:
        output = []
        for sentence in sentencesChunks:

            sentenceNoStopwords = []

            try:
                for token in word_tokenize(sentence, language="danish"):
                    if token.lower() not in dk_Stopwords:
                        sentenceNoStopwords.append(token.strip())

                sentenceClear = " ".join(sentenceNoStopwords).strip()
                output.append(sentenceClear)

            except Exception as e:
                print("removeStopwordsFromString error: could not remove stopwords due to :", e)

        finalOutput.append(" ".join(output))

    return " ".join(finalOutput)


def extractNE(textData, verbose=False):

    # Create a list of collocations
    collocationsList = [" ".join(bits for bits in chunk) for chunk in getCollocations(textData)]

    # and extract named entities from collocations
    NEcollocations = collectNamedEntities(" - ".join(collocationsList))  + nltkGit(" - ".join(collocationsList))

    # Extract the named entities via two methods
    NEcollection = collectNamedEntities(textData) + nltkGit(textData)

    # Merge all three Methods
    mergedNEs = NEcollection + NEcollocations

    # Create counter object
    NEcounter = [[data, id] for id, data in Counter(mergedNEs).items()]

    # Prune the NEcounter object to remove dublicates (could refine this mor)
    NEdata =  pruneNECollection(NEcounter)

    if verbose:
        print("Newlist      ",  Counter(NEdata))
        print()

    return NEdata


def getCollocations(stringContent, freq_filter=2, bigram_measures_pmi=20):

    #stringNoPuncuation = tokenizeRemovePunctuation(str(cleanAndBuild(soup, ".article__summary")).strip())
    #stringNoStopNoPunct = [word for word in stringNoPuncuation if word.lower() not in dk_Stopwords]

    #print("stringerbell", stringNoPuncuation)
    # Find collocations spanning over four words
    finder = TrigramCollocationFinder.from_words(word_tokenize(stringContent), window_size=3)

    # Must occur at least three times
    finder.apply_freq_filter(freq_filter)

    # Add the twenty top most collocations to a list
    trigramCollocations = finder.nbest(bigram_measures.pmi, bigram_measures_pmi)

    #print( "trigrams:   ", trigramCollocations)

    return trigramCollocations




def pruneNECollection(listItems):

    # print("     listitems", listItems)
    seenList = []
    removeDict = {}
    for item in listItems:
        for reversedItem in sorted(listItems, reverse=True):
            score = fuzz.ratio(item, reversedItem)
            if score > 90 and score < 100 and reversedItem[1] not in seenList:
                # print(score, item, reversedItem)
                shortest = list([item, reversedItem])
                # print(shortest)
                removeIt = sorted(list(shortest), reverse=True)[0][1]
                keep = sorted(list(shortest), reverse=True)[1][1]
                # print("R-K", removeIt, " -> ", keep)
                seenList.append(removeIt)
                try:
                    removeDict[removeIt] = keep
                except Exception as e:
                    pass
                # print("remove dict", removeDict)

    counter = 0
    newlist, deadstuff = [], []

    for itemkey in listItems:

        if removeDict.get(itemkey[1]):
            # print("found itemkey", itemkey)
            try:
                for rounds in range(int(itemkey[0])):
                    newlist.append(removeDict.get(itemkey[1]))
            except Exception as e:
                print("Error on removal", e)

            # print("adding to deadstuff ->:", listItems[counter][1])
            deadstuff.append(listItems[counter][1])

        else:
            if itemkey[1] not in deadstuff:
                try:
                    for rounds in range(int(itemkey[0])):
                        newlist.append(itemkey[1])
                except Exception as e:
                    print("Error on adding", e)

        counter += 1

    # print("newlist", newlist)
    return newlist



def nltkGit(sample):

    sentences = nltk.sent_tokenize(removeStopwords(sample),language="danish")
    tokenized_sentences = [nltk.word_tokenize(sentence,language="danish") for sentence in sentences]
    tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
    chunked_sentences = nltk.chunk.ne_chunk_sents(tagged_sentences, binary=True)

    def extract_entity_names(t):
        entity_names = []

        if hasattr(t, 'label') and t.label:
            if t.label() == 'NE':
                entity_names.append(' '.join([child[0] for child in t]))
            else:
                for child in t:
                    entity_names.extend(extract_entity_names(child))

        return entity_names

    entity_names = []
    for tree in chunked_sentences:
        #print("tree", tree)
        # Print results per sentence

        #print("EXO", extract_entity_names(tree))

        entity_names.extend(extract_entity_names(tree))

    # Print all entity names
    #print("EX2", entity_names)

    # Print unique entity names
    return entity_names


def removeStopwords(stringToREMOVEstopwordsFrom):

    if isinstance(stringToREMOVEstopwordsFrom, list):
        joinedList = ' '
        joinedList += " ".join(stringToREMOVEstopwordsFrom)
        stringToREMOVEstopwordsFrom = joinedList

    # dk_Stopwords = stopwords.words('danish')

    stringWithoutStopWords = ""

    for unique in stringToREMOVEstopwordsFrom.split():
        if unique not in dk_Stopwords:
            stringWithoutStopWords += "{} ".format(unique)

    return stringWithoutStopWords



def collectNamedEntities(stringToSearchIn):

    #  First we tokenise all the sentences
    tokenizedText = word_tokenize(stringToSearchIn,language="danish")
    #print("Tokenized Articles   ", tokenizedText)


    ##########################
    ### First do own setup ###

    # Collect Trigrams
    trigramText = list(trigrams(tokenizedText))
    #print("Trigrams", trigramText)

    count = 0
    namedEntityList = []
    for trigram in trigramText:

        # Trigrams
        try:
            if not trigram[0].islower() and not trigram[1].islower() and not trigram[2].islower() \
                    and trigram[0].isalpha() and trigram[1].isalpha() and trigram[2].isalpha():
                namedEntityList.append("{} {} {}".format( trigram[0], trigram[1], trigram[2]) )
        except Exception as e:
            print("Trigrams", e)

        # Bigrams
        try:
            if not trigram[0].islower() and not trigram[1].islower()  \
                    and trigram[0].isalpha() and trigram[1].isalpha()  and trigram[0].lower() not in dk_Stopwords:
                namedEntityList.append("{} {}".format( trigram[0], trigram[1] ) )
        except Exception as e:
            print("Bigrams", e)

        # singles
        try:
            if not trigram[0].islower() and not trigram[0].isupper()   \
                    and trigram[0].isalpha() and trigram[1].isalpha() and trigram[2].isalpha()  and trigram[0].lower() not in dk_Stopwords:
                namedEntityList.append("{}".format( trigram[0] ) )
        except Exception as e:
            print("Singles", e)

        # Trigrams with Digits at the end
        try:
            if not trigram[0].islower() and not trigram[1].isupper() and trigram[2].isdigit()  \
                    and trigram[0].isalpha() and trigram[1].isalpha() and trigram[2].isalpha()  and trigram[0].lower() not in dk_Stopwords:
                namedEntityList.append("{} {}".format( trigram[0], trigram[1] ) )
        except Exception as e:
            print("Trigrams Digits", e)

        # ABBR and Title
        try:
            if not trigram[0].islower() and trigram[1].islower() and trigram[2].islower() \
                    and trigram[0].isalpha() and trigram[1].isalpha() and trigram[2].isalpha():
                if trigram[0].isupper() and trigram[0].lower() not in dk_Stopwords:
                    namedEntityList.append("{}".format( trigram[0] ) )

                if trigram[0].istitle() and trigramText[count] != 0  and trigram[0].lower() not in dk_Stopwords\
                        or trigram[0] != trigramText[count-1][1]:
                    namedEntityList.append("{}".format( trigram[0] ) )
        except Exception as e:
            print("ABBR", e)


        # quadgrams and more - looking backwards
        # Quadgrams
        try:
            if not trigram[0].islower() and not trigram[1].islower() and not trigram[2].islower() \
                    and trigram[0].isalpha() and trigram[1].isalpha() and trigram[2].isalpha()\
                    and trigramText[count] != 0 and not trigramText[count-1][0].islower() and trigramText[count-1][0].isalpha():
                namedEntityList.append("{} {} {} {}".format( trigramText[count-1][0], trigram[0], trigram[1], trigram[2]) )
        except Exception as e:
            print("Quadgrams", e)

        # Cincograms
        try:
            if not trigram[0].islower() and not trigram[1].islower() and not trigram[2].islower() \
                    and trigram[0].isalpha() and trigram[1].isalpha() and trigram[2].isalpha()\
                    and trigramText[count] != 0 and trigramText[count] != 1 \
                    and not trigramText[count-2][0].islower() and not trigramText[count-2][1].islower() \
                    and trigramText[count-2][0].isalpha() and trigramText[count-2][1].isalpha():
                namedEntityList.append("{} {} {} {} {}".format( trigramText[count-2][0], trigramText[count-2][1], trigram[0], trigram[1], trigram[2]) )
        except Exception as e:
            print("cinogram", e)

        # Update counter for looking forward or backward
        count += 1


    ##########################
    ### Do correct process ###

    # Do Part of Speach tagging of all elements.
    posTags = pos_tag(stringToSearchIn.split())
    # print("POS                  ", posAllArticles)
    #print("posTagss", posTags)


    # Chunk the sentences and find Named Entities
    neTags = ne_chunk(posTags)
    # print("NE Articles          ", neAllArticles)
    # print("neTags" , neTags)

    collectedNE = []
    for wordTags in neTags:

        if isinstance(wordTags, tree.Tree):

            #print(wordTags)
            realWord = ""
            for realTag in wordTags:
                realWord += "{} ".format(realTag[0])


            # Convert wordTags to string to be able to search
            if "GPE" in str(wordTags):

                collectedNE.append(realWord.strip())
                #print("gpe      ", wordTags)

            elif "ORGANIZATION" in str(wordTags):

                collectedNE.append(realWord.strip())
                #print("Orgs     ", wordTags)

            elif "PERSON" in str(wordTags):

                collectedNE.append(realWord.strip())
                #print("Person   ", wordTags)

    #print("Named Entities Counter", Counter(collectedNE))
    ##########################################################################
    ### Process and remove stopwords and "wrong" words from homegrown list ###

    wrongWords = ['Ifølge' , 'Siden' ,'Afgørelsen', 'Ofte' ,'Bank','Big','Big Fat','Bank Arena','Frederikshavns','Handlingsplanen','Havvind','Historien','Liberal','Ligestillingsminister Manu Sareen','Metro Team','Nationale Forskningscenter','Realkredit','Rockwool','Saxo','udbrede,','Chefkonsulent Berit','Chefkonsulent Berit Toft','Esbjergenserne', 'Fondens Forskningsenhed','Chefkonsulent','Dagbladenes', 'Aktiviteten', 'Retten','Dansk','Allerede','Alligevel','Almindelige','Altså','Andre','Atleterne','Atleternes','Bachs','Bilen','Blandt','Hver','Hvilken','Hvordan','Hvorfor','Høje','Brug','Børnene','Center','Copenhagen Metro Team Sigurd','Dagens','Danmarks','Mens', 'Offeret' , 'Offerets' , 'Ofte' , 'Omegn' , 'Omkostningsreduktioner' , 'Omvendt' , 'Oven' , 'Overfald' , 'Paradoksalt' , 'Politiassistent' , 'Politiassistent Jacob' , 'Presset' , 'Prinsessen' , 'Problemet' , 'Præcis' , 'Pædagogik' , 'Realkreditrådets' , 'Reel' , 'Regeringens' , 'Rekord' , 'Resten' , 'Resultatet' , 'Retssagen' , 'Riskær Pedersens', 'Rungsted Kasper' , 'Rungsted Kasper Degn' , 'Sagen' , 'Samlet' , 'Samme' , 'Samtidig' , 'Scoringer' , 'Selve' , 'Selvfølgelig' , 'Selvom' , 'Senere' , 'Senest' , 'Siden' , 'Siden Thomas' , 'Siden Thomas Bach' , 'Skader' , 'Skatteminister' , 'Skatteminister Benny' , 'Skatteminister Benny Engelbrecht' , 'Skatteministeren' , 'Skole' , 'Skolen' , 'Skudt' , 'Sluttede' , 'Små', 'Socialdemokraterne Rasmus' , 'Socialdemokraterne Rasmus Horn' , 'Socialdemokraterne Rasmus Horn Langhoff' , 'Stat' , 'Store' , 'Strafferammen' , 'Stupid Man' , 'Svaret', 'Så' , 'Således' , 'Særlig', 'Team Sigurd' , 'Tidligere' , 'Tilbage' , 'Tilsynet' , 'To' , 'Tre' , 'Tror' , 'Tutoring' , 'Uddannelse' , 'Uden' , 'Umiddelbart' , 'Undersøgelserne' , 'Undervisning' , 'Undervisningen','Ved' , 'Vent' , 'Vælgerne', 'Økonomien' , 'Ønskeseddel' , 'Ønskesedlen' , 'Øster', 'Østerbro Historien' , 'Østre' ,'Mere', 'Metoden', 'Mindre', 'Modellen', 'Måske', 'Nationale','Nemlig', 'Netop', 'Nøglen', 'Objektiviteten','OL Okay', 'Danskerne','Desuden','Fire', 'Hovedentreprenøren', 'Flere', 'Fokus','Forbedret','Forinden','Formanden','Forskellene','Forskerne','Hjemmeholdet','Forskernes','Forskningscenter','Før','Ganske', 'Generelt','Godt','Giv','Hav','Dermed','Derfor','Derefter','Degns', 'Ideen','Idrætten','Idrættens','Ifølge','Dolken','Dommerne','Dårlig','Ekstra','Endelig','Ens','Indvandrere','Intet','Især','Journalisternes','Kan','Kniven','Kommunerne','Kommune','Københavns','Ledelsen','Landsret','Lidt','Lige','Ligestillingsminister','Ligestillingsminister Manu','Ligestillingsordfører','Listen','Loven','Lærerne','Læsefærdigheder','Magtens','Manden','Markedet','Matematiklæreren','Meldingen','Enten','Faresignaler Men','Faresignaler','Ekstra' , 'Institut', 'Uddannelse', 'Center', 'Café', 'Skudt' , 'Mindre' , 'Danmark om,', 'Ifølge Thomas Adelskov', 'Måske', 'Danske' , 'Særlig' , 'Hvorfor' , 'Dertil' , 'Han' , 'Skal' , 'Byggebranchen' , 'Danmark om' , 'Metoden' , 'Nemlig' , 'Eller' , 'Hvis' , 'Selvom' , 'Samtidig' , 'Nogle' , 'Derfor' , 'Den' , 'Derefter' , 'Alligevel' , 'Faresignaler Men' , 'Blandt' , 'Hvordan' , 'Nøglen' , 'Lederen' , 'Københavns Omegn' , 'skride.' , 'udbrede' , 'Danmarks', 'Danmark bagud. For', 'Hernings mål. Scoringer', 'gøre". Thomas Adelskov', 'Forskernes', 'Kommunernes' ]

    # Correct the misspellings and plurals mismatches
    namedEntityListCorrected    = [tag.replace("Alternativets", "Alternativet").replace("Rockwool Fondens", "Rockwool Fonden").replace("Metro Team Sigurd", "Copenhagen Metro Team").replace("Copenhagen Metro Team Sigurd", "Copenhagen Metro Team").replace("Socialdemokraterne Rasmus Horn Langhoff", "Rasmus Horn Langhoff").replace("Hovedentreprenøren CMT", "CMT").replace("I Realkredit Danmark", "Realkredit Danmark").replace("Men Jacob Bundsgaard", "Jacob Bundsgaard").replace("Metroselskabets", "Metroselskabet").replace("Hos Realkredit Danmark", "Realkredit Danmark").replace('Hjemmeholdet Frederikshavn', 'Frederikshavn').replace("Hernings", "Herning").replace("Ifølge Berlingske", "Berlingske").replace("Ifølge Jens", "Jens").replace("Ifølge Jens Rise", "Jens Rise").replace("Ifølge Jens Rise Rasmussen", "Jens Rise Rasmussen").replace("Ifølge Thomas", "Thomas").replace("Klaus Riskær Pedersens", "Klaus Riskær Pedersen").replace("Kasper Degns", "Kasper Degn").replace("Ifølge Thomas Adelskov", "Thomas Adelskov").replace("Finlands", "Finland").replace("Thomas Bachs", "Thomas Bach").replace("Skatteminister Benny Engelbrecht", "Benny Engelbrecht").replace("Anklagemyndighedens", "Anklagemyndigheden").replace("Siden Thomas Bach", "Thomas Bach").replace("KL&apos;s", "KL") for tag in namedEntityList if tag not in wrongWords]
    collectedNECorrected        = [tag.replace("Alternativets", "Alternativet").replace("Rockwool Fondens", "Rockwool Fonden").replace("Metro Team Sigurd", "Copenhagen Metro Team").replace("Copenhagen Metro Team Sigurd", "Copenhagen Metro Team").replace("Socialdemokraterne Rasmus Horn Langhoff", "Rasmus Horn Langhoff").replace("Hovedentreprenøren CMT", "CMT").replace("I Realkredit Danmark", "Realkredit Danmark").replace("Men Jacob Bundsgaard", "Jacob Bundsgaard").replace("Metroselskabets", "Metroselskabet").replace("Hos Realkredit Danmark", "Realkredit Danmark").replace('Hjemmeholdet Frederikshavn', 'Frederikshavn').replace("Hernings", "Herning").replace("Ifølge Berlingske", "Berlingske").replace("Ifølge Jens", "Jens").replace("Ifølge Jens Rise", "Jens Rise").replace("Ifølge Jens Rise Rasmussen", "Jens Rise Rasmussen").replace("Ifølge Thomas", "Thomas").replace("Klaus Riskær Pedersens", "Klaus Riskær Pedersen").replace("Kasper Degns", "Kasper Degn").replace("Ifølge Thomas Adelskov", "Thomas Adelskov").replace("Finlands", "Finland").replace("Thomas Bachs", "Thomas Bach").replace("Skatteminister Benny Engelbrecht", "Benny Engelbrecht").replace("Anklagemyndighedens", "Anklagemyndigheden").replace("Siden Thomas Bach", "Thomas Bach").replace("KL&apos;s", "KL") for tag in collectedNE if tag not in wrongWords]

    collectedNEFull = []
    [collectedNEFull.append(items) for items in namedEntityListCorrected]
    [collectedNEFull.append(items) for items in collectedNECorrected]

    return collectedNE




def rePrune(namedEntityList):
    """ Deals with aggregated almost duplicates from bad coding!, uses the fuzzywuzzy library
    :param namedEntityList: a list of named Entities
    :return: a pruned collection (list)
    """
    toBePruned = [[num, ne] for ne, num in Counter(namedEntityList).items()]
    return pruneNECollection(toBePruned)


def keepThoseAboveQuartile(bagname, outputQuartiles=False):

    numlist = [num for id, num in Counter(rePrune(bagname)).items()]

    if len(numlist) >= 3:

        try:
            quarts = float(np.percentile(numlist, 25)), float(np.percentile(numlist, 50)), float(np.percentile(numlist, 75))
            okayedNE = {id:num for id, num in Counter(rePrune(bagname)).items() if num >= quarts[1]}
            if outputQuartiles == True:
                return okayedNE, quarts
            else:
                return okayedNE
        except Exception as e:
            print("Cant return those above quartile {} ... -> due to : {}".format(bagname[:3], e) )

    else:
        try:
            if outputQuartiles == True:
                return {id:num for id, num in Counter(rePrune(bagname)).items()}, None
            else:
                return {id:num for id, num in Counter(rePrune(bagname)).items()}
        except Exception as e:
            print("Cant return those above quartile {} ... -> due to : {}".format(bagname[:3], e) )


def signal(neList):
    """ Note that this only looks at the NE list, and not the entire article, and as such does not currently represent
    the entirely actual truth about the signals form
    :param neList: the tokenized list to search for signals in
    :return: a dict with the forms of the NE  (ascending, descending, solid, diamond, hourglass)
    """
    seen = []
    shapeList = []
    outputDict = {}

    for namedEntity in neList:
        if namedEntity not in seen:

            # Build a list of binaries as signals, denoting presence (1) or absence (0)
            signalList = []

            for newitem in neList:

                if newitem == namedEntity:
                    signalList.append(1)
                else:
                    signalList.append(0)

            # No need to do the same thing for named entities that appear many times, so add it to a seen-list
            seen.append(namedEntity)

            # if there are more than three named entities (duplicates included) we can divide our list by three.
            if len(neList) >= 3:

                # Divide the list into three "equally" large chunks of head, torso and tail
                oneThird = int(round(len(neList)/3,0))
                head = signalList[:oneThird]
                torso = signalList[oneThird:(oneThird+oneThird)]
                tail = signalList[(oneThird+oneThird):]

                # Go through the sum of each chunk and describe it's shape (descending, ascending, diamond, hourglass, solid)
                if sum(head) < sum(torso) > sum(tail):
                    shape = "diamond"
                elif sum(head) >= sum(torso) > sum(tail):
                    shape = "descending"
                elif sum(head) > sum(torso) >= sum(tail):
                    shape = "descending"
                elif sum(head) < sum(torso) < sum(tail):
                    shape = "ascending"
                elif sum(head) < sum(torso) <= sum(tail):
                    shape = "ascending"
                elif sum(head) <= sum(torso) < sum(tail):
                    shape = "ascending"
                elif sum(head) > sum(torso) < sum(tail):
                    shape = "hourglass"
                elif sum(head) == sum(torso) == sum(tail):
                    shape = "solid"
                else:
                    # Adding a catch all, so far it has not been used...
                    shape = "unresolved!"

                # Add the shape to a list
                shapeList.append(shape)

                # If the named entity is seen more than once add to the output dict.
                if (sum(head) + sum(torso) + sum(tail) ) > 1:
                    outputDict[namedEntity] = {"sum" : (sum(head) + sum(torso) + sum(tail) ), "shape" : shape}
                else:
                    # Pass if 1 - need to keep noise down :)
                    pass

    # Also return a Counter object for the states. Not sure if I will use it.
    # !!! N.B. State Counter Object can be calculate vis SQL, no need to create an extra table !!!
    return outputDict

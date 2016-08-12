from SpaceDock.objects import Mod, ModVersion, User, Game, GameVersion
from SpaceDock.database import db
from SpaceDock.config import _cfg
from sqlalchemy import or_, and_, desc
from flask import session
import html
from urllib.parse import unquote
import math

from datetime import datetime

def weigh_result(result, terms):
    # Factors considered, * indicates important factors:
    # Mods where several search terms match are given a dramatically higher rank*
    # High followers and high downloads get bumped*
    # Mods with a long version history get bumped
    # Mods with lots of screenshots or videos get bumped
    # Mods with a short description get docked
    # Mods lose points the longer they go without updates*
    # Mods get points for supporting the latest KSP version
    # Mods get points for being open source
    # New mods are given a hefty bonus to avoid drowning among established mods
    score = 0
    name_matches = short_matches = 0
    for term in terms:
        if result.name.lower().count(term) != 0:
            name_matches += 1
            score += name_matches * 100
        if result.short_description.lower().count(term) != 0:
            short_matches += 1
            score += short_matches * 50
        for term in (tag.name for tag in result.tags):
            score += 1000
    score *= 100

    score += result.follower_count * 10
    score += result.download_count
    score += len(result.versions) / 5
    score += len(result.media)
    if len(result.description) < 100:
        score -= 10
    if result.updated:
        delta = (datetime.now() - result.updated).days
        if delta > 100:
            delta = 100 # Don't penalize for oldness past a certain point
        score -= delta / 5
    if result.source_link:
        score += 10
    if (result.created - datetime.now()).days < 30:
        score += 100

    return score

def search_mods(ga, text, page, limit):
    ###
    text = unquote(text)
    query = db.query(Mod).join(Mod.user).join(Mod.versions).join(Mod.game)
    filters = list()
    terms = text.strip('\t\n\r').lower().split(',')
    order_by_score = False
    for term in terms:
        # Trim the sides of the search query
        term = term.strip('\t\n\r')
        term = term.strip(' ')
        # Or
        """
        if ' or ' in term:
            or_filter = list()
            # Split the or query by the or substring
            or_terms = term.split(' or ')
            for or_term in or_terms:
                or_term = term.strip('\t\n\r')
                tags_to_or = list()
                # Find the tag in the database by it's name, the ilike here denotes case insensitvity
                or_tag = Tag.query.(Tag.name.ilike(or_term)).first()
                # If the tag exists add it to the filter
                if or_tag:
                    or_filter.append(or_tag)
                    # Make all tag filters into an or filter a  nd add it to the global filter
                    filters.append(_or(*or_filter))
                    continue
                    # Order by score
                    """
        if term == "order by score":
            order_by_score = True
            #query = Image.query.filter(filters)
        elif term.startswith("ver:"):
            filters.append(Mod.versions.any(ModVersion.gameversion.has(GameVersion.friendly_version == term[4:])))
        elif term.startswith("user:"):

            filters.append(User.username.ilike(term[5:]))
        elif term.startswith("game:"):
            filters.append(Mod.game_id == int(term[5:]))
        elif term.startswith("downloads:>"):
            filters.append(Mod.download_count > int(term[11:]))
        elif term.startswith("downloads:<"):
            filters.append(Mod.download_count < int(term[11:]))
        elif term.startswith("followers:>"):
            filters.append(Mod.follower_count > int(term[11:]))
        elif term.startswith("followers:<"):
            filters.append(Mod.follower_count < int(term[11:]))
        else:
            filters.append(Mod.tags.any(name=term))
            filters.append(Mod.name.ilike('%' + term + '%'))
            filters.append(User.username.ilike('%' + term + '%'))
            filters.append(Mod.short_description.ilike('%' + term + '%'))
    if ga:
        query = query.filter(Mod.game_id == ga.id)
    query = query.filter(or_(*filters))
    query = query.filter(Mod.published == True)
    query = query.order_by(desc(Mod.follower_count)) # We'll do a more sophisticated narrowing down of this in a moment
    total = math.ceil(query.count() / limit)
    if page > total:
        page = total
    if page < 1:
        page = 1
    results = sorted(query.all(), key=lambda r: weigh_result(r, terms), reverse=True)
    return results[(page - 1) * limit:page * limit], total

def search_users(text, page):
    terms = text.split(' ')
    query = db.query(User)
    filters = list()
    for term in terms:
        filters.append(User.username.ilike('%' + term + '%'))
        filters.append(User.description.ilike('%' + term + '%'))
        filters.append(User.forumUsername.ilike('%' + term + '%'))
        filters.append(User.ircNick.ilike('%' + term + '%'))
        filters.append(User.twitterUsername.ilike('%' + term + '%'))
        filters.append(User.redditUsername.ilike('%' + term + '%'))
    query = query.filter(or_(*filters))
    query = query.filter(User.public == True)
    query = query.order_by(User.username)
    query = query.limit(100)
    results = query.all()
    return results[page * 10:page * 10 + 10]

def typeahead_mods(text):
    query = db.query(Mod)
    filters = list()
    filters.append(Mod.name.ilike('%' + text + '%'))
    query = query.filter(or_(*filters))
    query = query.filter(Mod.published == True)
    query = query.order_by(desc(Mod.follower_count)) # We'll do a more sophisticated narrowing down of this in a moment
    results = sorted(query.all(), key=lambda r: weigh_result(r, text.split(' ')), reverse=True)
    return results

def search_users(text, page):
    terms = text.split(' ')
    query = db.query(User)
    filters = list()
    for term in terms:
        filters.append(User.username.ilike('%' + term + '%'))
        filters.append(User.description.ilike('%' + term + '%'))
        filters.append(User.forumUsername.ilike('%' + term + '%'))
        filters.append(User.ircNick.ilike('%' + term + '%'))
        filters.append(User.twitterUsername.ilike('%' + term + '%'))
        filters.append(User.redditUsername.ilike('%' + term + '%'))
    query = query.filter(or_(*filters))
    query = query.filter(User.public == True)
    query = query.order_by(User.username)
    query = query.limit(100)
    results = query.all()
    return results[page * 10:page * 10 + 10]

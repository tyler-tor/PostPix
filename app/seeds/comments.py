from app.models import db, Comment


def seed_comments(users, posts):
    """users/posts: {seed number: row} from seed_users()/seed_posts()."""
    comment1 = Comment(
        user_id=users[1].id,
        post_id=posts[2].id,
        body='this is a comment from user 1 for post2'
    )
    comment2 = Comment(
        user_id=users[2].id,
        post_id=posts[3].id,
        body='this is a comment from user 2 for post3'
    )
    comment3 = Comment(
        user_id=users[3].id,
        post_id=posts[1].id,
        body='this is a comment from user 3 for post1'
    )
    comment4 = Comment(
        user_id=users[4].id,
        post_id=posts[3].id,
        body='sick post bruh'
    )

    comment5 = Comment(
        user_id=users[4].id,
        post_id=posts[4].id,
        body='huh looks kinda bad'
    )
    comment6 = Comment(
        user_id=users[4].id,
        post_id=posts[5].id,
        body='meh'
    )

    comment7 = Comment(
        user_id=users[5].id,
        post_id=posts[4].id,
        body='Its ok i guess'
    )

    comment8 = Comment(
        user_id=users[5].id,
        post_id=posts[6].id,
        body='didnt work though?'
    )
    comment9 = Comment(
        user_id=users[6].id,
        post_id=posts[7].id,
        body='huh interesting'
    )
    comment10 = Comment(
        user_id=users[6].id,
        post_id=posts[6].id,
        body='hey i used this!'
    )
    comment11 = Comment(
        user_id=users[6].id,
        post_id=posts[8].id,
        body='hard to time tbh but im goinna write more for more content! if this bleeds its a good thing to test!!!!'
    )

    comment12 = Comment(
        user_id=users[7].id,
        post_id=posts[1].id,
        body='whats going on now? Longer comments to make sure noithing weird is going on'
    )

    comment13 = Comment(
        user_id=users[7].id,
        post_id=posts[3].id,
        body='noice'
    )

    comment14 = Comment(
        user_id=users[8].id,
        post_id=posts[12].id,
        body='i cant do it but im gonna keep typing to make sure there no weird css stuff going on!'
    )

    comment15 = Comment(
        user_id=users[8].id,
        post_id=posts[7].id,
        body='whoa nice! whoa nicewhoa nicewhoa nice'
    )

    comment16 = Comment(
        user_id=users[8].id,
        post_id=posts[10].id,
        body='hehe whatever whatever whatever whatever'
    )

    comment17 = Comment(
        user_id=users[9].id,
        post_id=posts[14].id,
        body='hehe whatever This is gonna be a much longer comment to test the styling so we can check to make sure there is not any content bleeding.'
    )
    comment18 = Comment(
        user_id=users[9].id,
        post_id=posts[8].id,
        body='heya'
    )
    comment19 = Comment(
        user_id=users[9].id,
        post_id=posts[13].id,
        body='nooooo'
    )

    comment20 = Comment(
        user_id=users[10].id,
        post_id=posts[1].id,
        body='hey nice!'
    )
    comment21 = Comment(
        user_id=users[10].id,
        post_id=posts[6].id,
        body='not bad?'
    )
    comment22 = Comment(
        user_id=users[10].id,
        post_id=posts[4].id,
        body='its ok'
    )
    comment23 = Comment(
        user_id=users[10].id,
        post_id=posts[20].id,
        body='more seed data?'
    )
    comment24 = Comment(
        user_id=users[5].id,
        post_id=posts[20].id,
        body='editing the stuff is hard'
    )
    comment25 = Comment(
        user_id=users[6].id,
        post_id=posts[21].id,
        body='I barely use this one'
    )
    comment26 = Comment(
        user_id=users[6].id,
        post_id=posts[17].id,
        body='nice!'
    )
    comment27 = Comment(
        user_id=users[7].id,
        post_id=posts[16].id,
        body='woooooooooooo'
    )
    # ---------------------------------------------------------------------
    comment28 = Comment(
        user_id=users[1].id,
        post_id=posts[30].id,
        body='It took him a month to finish the meal.'
    )
    comment29 = Comment(
        user_id=users[1].id,
        post_id=posts[25].id,
        body='Ive never seen a more beautiful brandy glass filled with wine.'
    )
    comment30 = Comment(
        user_id=users[1].id,
        post_id=posts[27].id,
        body='If any cop asks you where you were, just say you were visiting Kansas.'
    )
    comment31 = Comment(
        user_id=users[2].id,
        post_id=posts[26].id,
        body='The secret code they created made no sense, even to them.'
    )
    comment32 = Comment(
        user_id=users[2].id,
        post_id=posts[41].id,
        body='Various sea birds are elegant, but nothing is as elegant as a gliding pelican.'
    )
    comment33 = Comment(
        user_id=users[2].id,
        post_id=posts[44].id,
        body='He put heat on the wound to see what would grow.'
    )
    comment34 = Comment(
        user_id=users[3].id,
        post_id=posts[49].id,
        body='Just go ahead and press that button.'
    )
    comment35 = Comment(
        user_id=users[3].id,
        post_id=posts[29].id,
        body='She did her best to help him.'
    )
    comment36 = Comment(
        user_id=users[3].id,
        post_id=posts[38].id,
        body='The paintbrush was angry at the color the artist chose to use.'
    )
    comment37 = Comment(
        user_id=users[15].id,
        post_id=posts[28].id,
        body='After exploring the abandoned building, he started to believe in ghosts.'
    )
    comment38 = Comment(
        user_id=users[15].id,
        post_id=posts[26].id,
        body='The llama couldnt resist trying the lemonade.'
    )
    comment39 = Comment(
        user_id=users[15].id,
        post_id=posts[24].id,
        body='She did not cheat on the test, for it was not the right thing to do.'
    )
    comment40 = Comment(
        user_id=users[14].id,
        post_id=posts[1].id,
        body='I want a giraffe, but Im a turtle eating waffles.'
    )
    comment41 = Comment(
        user_id=users[14].id,
        post_id=posts[2].id,
        body='The delicious aroma from the kitchen was ruined by cigarette smoke.'
    )
    comment42 = Comment(
        user_id=users[14].id,
        post_id=posts[3].id,
        body='He had concluded that pigs must be able to fly in Hog Heaven.'
    )
    comment43 = Comment(
        user_id=users[13].id,
        post_id=posts[4].id,
        body='Im confused: when people ask me whats up, and I point, they groan.'
    )
    comment44 = Comment(
        user_id=users[13].id,
        post_id=posts[5].id,
        body='Today arrived with a crash of my car through the garage door.'
    )
    comment45 = Comment(
        user_id=users[13].id,
        post_id=posts[6].id,
        body='Please put on these earmuffs because I cant you hear.'
    )
    comment46 = Comment(
        user_id=users[12].id,
        post_id=posts[7].id,
        body='Its not often you find a soggy banana on the street.'
    )
    comment47 = Comment(
        user_id=users[12].id,
        post_id=posts[8].id,
        body='Edith could decide if she should paint her teeth or brush her nails.'
    )
    comment48 = Comment(
        user_id=users[12].id,
        post_id=posts[9].id,
        body='He wondered if it could be called a beach if there was no sand.'
    )
    comment49 = Comment(
        user_id=users[11].id,
        post_id=posts[10].id,
        body='Jenny made the announcement that her baby was an alien.'
    )
    comment50 = Comment(
        user_id=users[11].id,
        post_id=posts[11].id,
        body='That was how he came to win $1 million.'
    )
    comment51 = Comment(
        user_id=users[11].id,
        post_id=posts[12].id,
        body='If any cop asks you where you were, just say you were visiting Kansas.'
    )
    comment52 = Comment(
        user_id=users[10].id,
        post_id=posts[13].id,
        body='The virus had powers none of us knew existed.'
    )
    comment53 = Comment(
        user_id=users[10].id,
        post_id=posts[14].id,
        body='Im a living furnace.'
    )
    comment54 = Comment(
        user_id=users[10].id,
        post_id=posts[15].id,
        body='He wasnt bitter that she had moved on but from the radish.'
    )
    comment55 = Comment(
        user_id=users[9].id,
        post_id=posts[16].id,
        body='The waves were crashing on the shore; it was a lovely sight.'
    )
    comment56 = Comment(
        user_id=users[9].id,
        post_id=posts[17].id,
        body='He had unknowingly taken up sleepwalking as a nighttime hobby.'
    )
    comment57 = Comment(
        user_id=users[9].id,
        post_id=posts[18].id,
        body='He stepped gingerly onto the bridge knowing that enchantment awaited on the other side.'
    )
    comment58 = Comment(
        user_id=users[8].id,
        post_id=posts[19].id,
        body='He was willing to find the depths of the rabbit hole in order to be with her.'
    )
    comment59 = Comment(
        user_id=users[8].id,
        post_id=posts[20].id,
        body='I had a friend in high school named Rick Shaw, but he was fairly useless as a mode of transport.'
    )
    comment60 = Comment(
        user_id=users[8].id,
        post_id=posts[21].id,
        body='The furnace repairman indicated the heating system was acting as an air conditioner.'
    )
    comment61 = Comment(
        user_id=users[7].id,
        post_id=posts[22].id,
        body='Random words in front of other random words create a random sentence.'
    )
    comment62 = Comment(
        user_id=users[7].id,
        post_id=posts[23].id,
        body='There have been days when I wished to be separated from my body, but today wasn’t one of those days.'
    )
    comment63 = Comment(
        user_id=users[7].id,
        post_id=posts[24].id,
        body='She had a difficult time owning up to her own crazy self.'
    )
    comment64 = Comment(
        user_id=users[6].id,
        post_id=posts[25].id,
        body='The bees decided to have a mutiny against their queen.'
    )
    comment65 = Comment(
        user_id=users[6].id,
        post_id=posts[26].id,
        body='The tortoise jumped into the lake with dreams of becoming a sea turtle.'
    )
    comment66 = Comment(
        user_id=users[6].id,
        post_id=posts[27].id,
        body='His confidence would have bee admirable if it wasnt for his stupidity.'
    )
    comment67 = Comment(
        user_id=users[5].id,
        post_id=posts[28].id,
        body='My biggest joy is roasting almonds while stalking prey.'
    )
    comment68 = Comment(
        user_id=users[5].id,
        post_id=posts[29].id,
        body='Too many prisons have become early coffins.'
    )
    comment69 = Comment(
        user_id=users[5].id,
        post_id=posts[30].id,
        body='Yeah, I think its a good environment for learning English.'
    )
    comment70 = Comment(
        user_id=users[4].id,
        post_id=posts[31].id,
        body='She wrote him a long letter, but he didnt read it.'
    )
    comment71 = Comment(
        user_id=users[4].id,
        post_id=posts[32].id,
        body='Theres an art to getting your way, and spitting olive pits across the table isnt it.'
    )
    comment72 = Comment(
        user_id=users[4].id,
        post_id=posts[33].id,
        body='There can never be too many cherries on an ice cream sundae.'
    )
    comment73 = Comment(
        user_id=users[3].id,
        post_id=posts[34].id,
        body='He enjoys practicing his ballet in the bathroom.'
    )
    comment74 = Comment(
        user_id=users[3].id,
        post_id=posts[35].id,
        body='Two seats were vacant.'
    )
    comment75 = Comment(
        user_id=users[3].id,
        post_id=posts[36].id,
        body='Nobody loves a pig wearing lipstick.'
    )
    comment76 = Comment(
        user_id=users[2].id,
        post_id=posts[37].id,
        body='She borrowed the book from him many years ago and hasnt yet returned it.'
    )
    comment77 = Comment(
        user_id=users[2].id,
        post_id=posts[38].id,
        body='He was sitting in a trash can with high street class.'
    )
    comment78 = Comment(
        user_id=users[2].id,
        post_id=posts[39].id,
        body='She did not cheat on the test, for it was not the right thing to do.'
    )
    comment79 = Comment(
        user_id=users[1].id,
        post_id=posts[40].id,
        body='I liked their first two albums but changed my mind after that charity gig.'
    )
    comment80 = Comment(
        user_id=users[1].id,
        post_id=posts[41].id,
        body='Im worried by the fact that my daughter looks to the local carpet seller as a role model.'
    )


    db.session.add(comment1)
    db.session.add(comment2)
    db.session.add(comment3)
    db.session.add(comment4)
    db.session.add(comment5)
    db.session.add(comment6)
    db.session.add(comment7)
    db.session.add(comment8)
    db.session.add(comment9)
    db.session.add(comment10)
    db.session.add(comment11)
    db.session.add(comment12)
    db.session.add(comment13)
    db.session.add(comment14)
    db.session.add(comment15)
    db.session.add(comment16)
    db.session.add(comment17)
    db.session.add(comment18)
    db.session.add(comment19)
    db.session.add(comment20)
    db.session.add(comment21)
    db.session.add(comment22)
    db.session.add(comment23)
    db.session.add(comment24)
    db.session.add(comment25)
    db.session.add(comment26)
    db.session.add(comment27)
    db.session.add_all([
        comment28,
        comment29,
        comment30,
        comment31,
        comment32,
        comment33,
        comment34,
        comment35,
        comment36,
        comment37,
        comment38,
        comment39,
        comment40,
        comment41,
        comment42,
        comment43,
        comment44,
        comment45,
        comment46,
        comment47,
        comment48,
        comment49,
        comment50,
        comment51,
        comment52,
        comment53,
        comment54,
        comment55,
        comment56,
        comment57,
        comment58,
        comment59,
        comment60,
        comment61,
        comment62,
        comment63,
        comment64,
        comment65,
        comment66,
        comment67,
        comment68,
        comment69,
        comment70,
        comment71,
        comment72,
        comment73,
        comment74,
        comment75,
        comment76,
        comment77,
        comment78,
        comment79,
        comment80
    ])

    db.session.commit()


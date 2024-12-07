(define (domain Iliad)
(:requirements :typing :negative-preconditions :equality)
(:types hero priest slave - human
	god human nymph - character		 
	location 
	disasters
	moods 
	types_of_interaction
) 

(:constants 
	good - moods
	bad - moods
	worried - moods
	neutral - moods
	resigned - moods
	trust - moods
	loyal - moods
	envy - moods
	request_release - moods
	desire_to_punish - moods
	accept_release - moods
	accept_punish - moods

	desire_cease_disaster - types_of_interaction
	request_release_interaction - types_of_interaction
	refuse_release - types_of_interaction
	accept_release_interaction - types_of_interaction
	request_punish - types_of_interaction
	accept_punish_interaction - types_of_interaction
	desire_capture - types_of_interaction
	block_the_attempt_to_kill - types_of_interaction
	attempt_to_kill - types_of_interaction
	meet - types_of_interaction
)


(:predicates 
(at ?x - character ?y - location)
(mood ?x1 - character ?x2 - character ?y - moods)
(related ?x1 - character ?x2 - character)
(disaster ?loc - location ?t - disasters ?g - god)
(captured ?c1 - character ?c2 - character)
(fake_effect)
(is_accept_release ?t)
)

(:action interact-self
:parameters (?c1 - character ?t - types_of_interaction ?c2 - character ?loc - location) 
:precondition (at ?c1 ?loc)
:effect (and (fake_effect)
 	     (forall (?g - god) (when (and (mood ?c1 ?c2 bad) (mood ?c2 ?c1 envy) (= ?t attempt_to_kill) (at ?c2 ?loc)  
		                      (mood ?g ?c1 good) (mood ?g ?c2 good) (at ?g ?loc)) 
				      (and (mood ?g ?c1 worried) (mood ?g ?c2 worried))))
	     (when (and (mood ?c1 ?c2 resigned) (= ?t accept_release_interaction) (captured ?c2 ?c1) (at ?c2 ?loc))
			(mood ?c1 ?c2 accept_release))
	     (when (and (mood ?c1 ?c2 desire_to_punish) (= ?t accept_punish_interaction)) 
			(mood ?c1 ?c2 accept_punish))
)
)

(:action interact-mood
:parameters (?c1 - character ?c2 - character ?t - types_of_interaction ?c3 - character ?loc - location) 
:precondition (at ?c1 ?loc)
:effect (and (fake_effect)
	     (when (and (mood ?c2 ?c1 neutral) (= ?t request_release_interaction) (related ?c1 ?c3) (captured ?c3 ?c2) (at ?c2 ?loc) (at ?c3 ?loc)) 
			(and (mood ?c1 ?c2 request_release) (mood ?c2 ?c1 bad)))
	     (when (and (mood ?c1 ?c2 bad)  (mood ?c2 ?c1 request_release) (= ?t refuse_release) (captured ?c3 ?c1) 
			(at ?c2 ?loc) (at ?c3 ?loc)) 
			(mood ?c2 ?c1 bad))
	     (when (and (mood ?c1 ?c3 bad) (mood ?c3 ?c1 bad) (mood ?c2 ?c1 good) (mood ?c2 ?c3 neutral) (= ?t request_punish) (at ?c2 ?loc)) 
			(mood ?c2 ?c3 desire_to_punish))
	     (when (and (mood ?c2 ?c1 trust) (= ?t request_release_interaction) (captured ?c3 ?c2) (at ?c2 ?loc)
		        (exists (?dis - disasters ?g - god) (disaster ?loc ?dis ?g))) 
			(mood ?c2 ?c3 resigned))
 	     (when (and (mood ?c1 ?c2 envy) (= ?t desire_capture) (captured ?c3 ?c2) (at ?c2 ?loc) (forall (?s - slave) (not (captured ?s ?c1)))) 
			(mood ?c2 ?c1 bad))
 	     (when (and (mood ?c1 ?c2 worried) (mood ?c1 ?c3 worried) (mood ?c2 ?c3 bad) (mood ?c3 ?c2 envy)  (= ?t block_the_attempt_to_kill)
			(at ?c2 ?loc) (at ?c3 ?loc))  
		        (and (mood ?c1 ?c2 good) (mood ?c1 ?c3 good) (mood ?c3 ?c2 bad)))
	     (forall (?h - hero) (when (and (mood ?h ?c1 loyal) (mood ?h ?c2 accept_release) (mood ?c3 ?h bad) (= ?t meet) 
					     (related ?c3 ?c2) (not (captured ?c2 ?h)) (at ?c2 ?loc)  (at ?c3 ?loc)) 
				       	     (mood ?c3 ?h good)))
	     (forall (?h - hero) (when (and (mood ?c3 ?h accept_punish) (mood ?c1 ?h good) (mood ?c3 ?c1 good) (mood ?h ?c2 loyal) 
					    (= ?t desire_cease_disaster) (at ?c3 ?loc) (at ?c2 ?loc)) 
				       	    (mood ?c3 ?h good)))
	     (when (and (mood ?c1 ?c3 bad) (mood ?c3 ?c1 bad) (mood ?c2 ?c1 good) (= ?t request_punish) (related ?c2 ?c1) 
		        (not (exists (?d - disasters ?l - location ?g - god) (disaster ?l ?d ?g)))) 
			(mood ?c2 ?c3 desire_to_punish))
	     (when (and (mood ?c1 ?c3 desire_to_punish) (related ?c2 ?c1) (= ?t request_punish)) 
			(and (mood ?c1 ?c3 bad) (mood ?c2 ?c3 desire_to_punish)))
)
)

;****************
;A human (which is not captured by any character) can move from a starting location *from* to a destination *to*.
;****************
(:action go
:parameters (?x - human ?from - location ?to - location) 
:precondition (and (at ?x ?from) (not (at ?x ?to)) (forall (?c2 - character) (not (captured ?x ?c2))) (not (exists (?c3 - character) (and (at ?c3 ?to) (mood ?c3 ?x bad)))))
:effect (and (not (at ?x ?from)) (at ?x ?to))
)

;****************
;A god *g*, if angry with a hero situated in location *loc*, can punish him by provoking a disaster *dis* in *loc*. 
;****************
(:action punish
:parameters (?g - god ?loc - location ?dis - disasters) 
:precondition (and (not (disaster ?loc ?dis ?g)))
:effect (disaster ?loc ?dis ?g)
)

(:action punish_hero
:parameters (?g - god ?h - hero ?loc - location ?dis - disasters) 
:precondition (and (not (disaster ?loc ?dis ?g)) (and (mood ?g ?h accept_punish) (at ?h ?loc)))
:effect (disaster ?loc ?dis ?g)
)

;****************
;A god *g* may decide to cease a disaster *dis* provoked by himself in location *loc* 
;if it is in good related with one of the heroes situated in *loc*. 
;****************
(:action cease_disaster
:parameters (?g - god ?loc - location ?dis - disasters) 
:precondition (and (disaster ?loc ?dis ?g) )
:effect (not (disaster ?loc ?dis ?g))
)

(:action cease_disaster_hero
:parameters (?g - god ?h - hero ?loc - location ?dis - disasters) 
:precondition (and (disaster ?loc ?dis ?g)  (and (mood ?g ?h good) (at ?h ?loc)))
:effect (not (disaster ?loc ?dis ?g))
)


;****************
;A hero *h* may decide to release a slave *sl* if he is resigned to lose her/him.
;****************
(:action release
:parameters (?h - hero ?sl - slave ?loc - location)  
:precondition (and (at ?h ?loc) (at ?sl ?loc) (captured ?sl ?h) (mood ?h ?sl accept_release))
:effect (not (captured ?sl ?h))
)

;****************
;A hero *h* may desire to capture a slave *sl* owned by another hero *h2*, if *h* is angry with *h1*.
;****************
(:action capture
:parameters (?h - hero ?sl - slave ?loc - location)  
:precondition (and (at ?h ?loc) (at ?sl ?loc))
:effect (and (forall (?h1 - hero) (not (captured ?sl ?h1))) (captured ?sl ?h))
)

(:action capture_hero
:parameters (?h - hero ?h1 - hero ?sl - slave ?loc - location)  
:precondition (and (at ?h ?loc) (at ?sl ?loc) (and (captured ?sl ?h1) (mood ?h ?h1 bad)))
:effect (and (forall (?h1 - hero) (not (captured ?sl ?h1))) (captured ?sl ?h))
)

)

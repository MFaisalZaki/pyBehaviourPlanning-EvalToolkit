(define (problem Book_1) (:domain Iliad)
(:objects
	Apollo - god
	Athene - god
	Zeus - god
	Thetis - nymph
	Achilleus - hero
	Agamemnon - hero
	Odysseus - hero
	Chryses - priest
	Kalchas - priest
	Chryseis - slave
	Briseis - slave

	

	plague - disasters

	Apollo_temple - location
	Greeks_camp - location
	Olympus - location
)
(:init
	(mood Agamemnon Chryses neutral)
	(mood Agamemnon Kalchas trust)
	(mood Agamemnon Odysseus loyal)
	(mood Agamemnon Achilleus envy)
	(mood Apollo Chryses good)
	(mood Apollo Agamemnon neutral)
	(mood Athene Achilleus good)
	(mood Athene Agamemnon good)
	(mood Thetis Achilleus good)

	(captured Briseis Achilleus)
	(captured Chryseis Agamemnon)

	(related Chryses Chryseis)
	(related Thetis Achilleus)
	(related Zeus Thetis)

	(at Achilleus Greeks_camp)
	(at Agamemnon Greeks_camp)
	(at Odysseus Greeks_camp)
	(at Chryses Apollo_temple)
	(at Kalchas Greeks_camp)
	(at Chryseis Greeks_camp)
	(at Briseis Greeks_camp)
	(at Apollo Apollo_temple)
	(at Thetis Greeks_camp)
	(at Athene Greeks_camp)
	(at Zeus Olympus)

)
(:goal 
	(and (mood Achilleus Agamemnon bad) (mood Zeus Agamemnon accept_punish) (mood Chryses Agamemnon good))
)	
)

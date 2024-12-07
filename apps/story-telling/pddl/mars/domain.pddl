(define (domain mars_exploration)

;remove requirements that are not needed
(:requirements :strips :typing :conditional-effects :equality :disjunctive-preconditions)

(:types ;todo: enumerate types and their hierarchy here, e.g. car truck bus - vehicle
    scientist engineer astronaut - human
    equipment
    sample_type
    location
)

; un-comment following line if constants are needed
(:constants
    base_station - location 
    soil air  - sample_type
)

(:predicates ;todo: define predicates here
    (operational ?e - equipment)
    (at ?c - human ?l - location)
    (is_valid_sample ?t - sample_type ?l - location)
    (sample_collected ?c - scientist ?t - sample_type ?l - location ?e - equipment)
    (traversable ?from - location ?to - location)
    (valid_samples_found ?t - sample_type)
    (containment ?l - location ?t - sample_type)
)

(:action navigate
    :parameters (?c - scientist ?from - location ?to - location)
    :precondition (and 
        (at ?c ?from)
        (traversable ?from ?to)
    )
    :effect (and 
        (at ?c ?to)
        (not (at ?c ?from))
    )
)


(:action sample
    :parameters (?c - scientist ?e - equipment ?l - location ?t - sample_type)
    :precondition (and (at ?c ?l))
    :effect (and 
        (when (and (at ?c ?l) (= ?t soil)) (sample_collected ?c soil ?l ?e))
        (when (and (at ?c ?l) (= ?t air))  (sample_collected ?c air  ?l ?e))
    )
)

(:action validate
    :parameters (?c - scientist ?e - equipment ?l - location ?t - sample_type)
    :precondition (and 
        (sample_collected ?c ?t ?l ?e) 
        (at ?c base_station)
    )
    :effect (and 
        (when (and (operational ?e) (not (containment ?l ?t))) (is_valid_sample ?t ?l))
        (when (or  (not (operational ?e)) (containment ?l ?t)) (not (is_valid_sample ?t ?l)))
    )
)

(:action report
    :parameters (?l - location ?t - sample_type)
    :precondition (and (is_valid_sample ?t ?l))
    :effect (and 
        (valid_samples_found ?t)
    )
)



; (:action sample_soil
;     :parameters (?c - scientist ?e - equipment ?l - location)
;     :precondition (and (at ?c ?l))
;     :effect (and 
;         (when (and (at ?c ?l) (operational ?e))       (and (sample_collected ?c soil ?l)       (is_valid_sample soil)))
;         (when (and (at ?c ?l) (not (operational ?e))) (and (not (sample_collected ?c soil ?l)) (not (is_valid_sample soil))))
;     )
; )

; We will have three actions: sample, analyze, report

)
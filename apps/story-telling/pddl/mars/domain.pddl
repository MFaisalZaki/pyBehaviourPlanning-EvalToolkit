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
    (contaminated ?l - location ?t - sample_type)
    (is_storm_at ?l - location)
    (mission_failed)
    (scanned_location ?l - location)
    (can_sample_soil ?e - equipment)
    (can_sample_air ?e - equipment)
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
    :precondition (and (at ?c ?l)
        (or (and (can_sample_soil ?e) (= ?t soil)) (and (can_sample_air ?e)  (= ?t air)))
    )
    :effect (and
        (scanned_location ?l) 
        (when (and (at ?c ?l) (= ?t soil)) (sample_collected ?c soil ?l ?e))
        (when (and (at ?c ?l) (= ?t air))  (sample_collected ?c air  ?l ?e))
    )
)

(:action validate
    :parameters (?c - scientist ?e - equipment ?l - location ?t - sample_type)
    :precondition (and 
        (sample_collected ?c ?t ?l ?e) 
        (at ?c base_station)
        (or (and (can_sample_soil ?e) (= ?t soil)) (and (can_sample_air ?e)  (= ?t air)))
    )
    :effect (and 
        (when (and (operational ?e) (not (contaminated ?l ?t))) (is_valid_sample ?t ?l))
        (when (or  (not (operational ?e)) (contaminated ?l ?t)) (not (is_valid_sample ?t ?l)))
    )
)

(:action report
    :parameters (?l - location ?t - sample_type)
    :precondition (and (is_valid_sample ?t ?l))
    :effect (and 
        (valid_samples_found ?t)
        (not (mission_failed))
    )
)

(:action abort_mission
    :parameters ()
    :precondition (and 
        (forall (?l - location ?t - sample_type) (and (scanned_location ?l) (not (is_valid_sample ?t ?l))))
    )
    :effect (and (mission_failed))
)


; What possibly could be the preconditions for a storm.
(:action storm_started
    :parameters (?l - location ?h - human)
    :precondition (and )
    :effect (and 
        (forall (?from - location) (not (traversable ?from ?l)))
        (forall (?to - location)  (not (traversable ?l ?to)))
        (is_storm_at ?l)
    )
)

(:action storm_ended
    :parameters (?l - location)
    :precondition (and (is_storm_at ?l))
    :effect (and 
        (forall (?from - location)  (traversable ?from ?l))
        (forall (?to - location)   (traversable ?l ?to))
        (not (is_storm_at ?l))
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
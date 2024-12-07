(define (domain mars_exploration)

;remove requirements that are not needed
(:requirements :strips :typing :conditional-effects :equality :negative-preconditions :disjunctive-preconditions)

(:types ;todo: enumerate types and their hierarchy here, e.g. car truck bus - vehicle
    scientist engineer astronaut - human
    equipment
    sample_type
    location
)

; un-comment following line if constants are needed
(:constants
    base_station space_ship - location 
    soil air  - sample_type
)

(:predicates ;todo: define predicates here
    (operational ?e - equipment)
    (at ?c - human ?l - location)
    (placed ?e - equipment ?l - location)
    (is_valid_sample ?t - sample_type ?l - location)
    (sample_collected ?c - scientist ?t - sample_type ?l - location ?e - equipment)
    (traversable ?from - location ?to - location)
    (valid_samples_found ?t - sample_type)
    (contaminated ?l - location ?t - sample_type)
    (is_storm_at ?l - location)
    (scanned_location ?l - location)
    (can_sample_soil ?e - equipment)
    (can_sample_air ?e - equipment)
    (storm_occurred)
    (mission_failed)
    (landed_space_ship)
    (is_sampling_location ?l - location ?t - sample_type)
)

(:action land_space_ship_and_deploy
    :parameters (?c - astronaut)
    :precondition (and 
        (not (landed_space_ship))
        (not (is_storm_at base_station)    
    )
    :effect (and 
        (forall (?c - human) (at ?c base_station))
        (forall (?c - human) (not (at ?c space_ship)))
        (forall (?e - equipment) (placed ?e base_station))
        (forall (?e - equipment) (not (placed ?e space_ship)))
        (landed_space_ship)
    )
)

(:action navigate
    :parameters (?c - human ?from - location ?to - location)
    :precondition (and
        (landed_space_ship) 
        (at ?c ?from)
        (traversable ?from ?to)
    )
    :effect (and 
        (at ?c ?to)
        (not (at ?c ?from))
    )
)

(:action move
    :parameters (?e - equipment ?from - location ?to - location)
    :precondition (and
        (landed_space_ship)  
        (placed ?e ?from)
        (traversable ?from ?to)
    )
    :effect (and 
        (placed ?e ?to)
        (not (placed ?e ?from))
    )
)

(:action sample
    :parameters (?c - scientist ?e - equipment ?l - location ?t - sample_type)
    :precondition (and 
        (landed_space_ship) 
        (at ?c ?l)
        (placed ?e ?l)
        (or 
            (and (can_sample_soil ?e) (is_sampling_location ?l soil) (= ?t soil)) 
            (and (can_sample_air ?e)  (is_sampling_location ?l air)  (= ?t air))
        )
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
        (landed_space_ship) 
        (sample_collected ?c ?t ?l ?e) 
        (at ?c base_station)
        (or 
            (and (can_sample_soil ?e) (is_sampling_location ?l soil) (= ?t soil)) 
            (and (can_sample_air ?e)  (is_sampling_location ?l air)  (= ?t air))
        )
    )
    :effect (and 
        (when (and (operational ?e) (not (contaminated ?l ?t))) (is_valid_sample ?t ?l))
        (when (or  (not (operational ?e)) (contaminated ?l ?t)) (not (is_valid_sample ?t ?l)))
    )
)

(:action report
    :parameters (?l - location ?t - sample_type)
    :precondition (and
        (landed_space_ship) 
        (is_valid_sample ?t ?l)    
    )
    :effect (and 
        (valid_samples_found ?t)
        (not (mission_failed))
    )
)

(:action abort_mission
    :parameters ()
    :precondition (and
        (landed_space_ship) 
        (forall (?l - location ?t - sample_type) (and (scanned_location ?l) (not (is_valid_sample ?t ?l))))
    )
    :effect (and (mission_failed))
)

(:action fix_equipment
    :parameters (?c - engineer ?e - equipment ?l - location)
    :precondition (and 
        (landed_space_ship) 
        (at ?c ?l)
        (placed ?e ?l)
        (not (operational ?e))
    )
    :effect (and 
        (operational ?e)
    )
)

; What possibly could be the preconditions for a storm.
(:action storm_started
    :parameters (?l - location)
    :precondition (and )
    :effect (and
        (is_storm_at ?l)
        (forall (?e - equipment) (when (placed ?e ?l) (not (operational ?e))))
        (storm_occurred)
    )
)

(:action storm_ended
    :parameters (?l - location)
    :precondition (and (is_storm_at ?l))
    :effect (and 
        (not (is_storm_at ?l))
    )
)

; (:action storm_break_equipment
;     :parameters (?l - location ?e - equipment)
;     :precondition (and (is_storm_at ?l))
;     :effect (and )
; )

; (:action break_equipment
;     :parameters (?e - equipment)
;     :precondition (and (not (operational ?e)))
;     :effect (and (operational ?e))
; )

; (:action fix_equipment
;     :parameters (?e - equipment)
;     :precondition (and (operational ?e))
;     :effect (and (not (operational ?e)))
; )

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
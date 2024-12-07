(define (problem scenario_1) (:domain mars_exploration)
(:objects 
    alex - scientist
    
    mountain1 mountain2 mountain3 - location
    soil_sampler_1 soil_sampler_2 - equipment
)

(:init
    (at alex base_station)
    (traversable base_station mountain1)
    (traversable mountain1 mountain2)
    (traversable mountain2 mountain3)
    (traversable mountain3 base_station)

    (operational soil_sampler_1)
    (operational soil_sampler_2)

    (can_sample_soil soil_sampler_1)
    (can_sample_soil soil_sampler_2)

    (contaminated base_station soil)
    (contaminated mountain1 soil)
    (contaminated mountain2 soil)
    (contaminated mountain3 soil)
)

(:goal (or
    ; (sample_collected alex soil mountain2)
    ; (at alex mountain2)
    (valid_samples_found soil)
    (mission_failed)
))

)

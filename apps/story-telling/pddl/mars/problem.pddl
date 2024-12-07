(define (problem scenario_1) (:domain mars_exploration)
(:objects 
    alex  - scientist
    camilla - engineer
    sally - astronaut
    
    mountain1 mountain2 mountain3 - location
    soil_sampler_1 - equipment
)

(:init
    (at alex space_ship)
    (at camilla space_ship)
    (at sally space_ship)
    (placed soil_sampler_1 space_ship)

    (is_sampling_location mountain1 soil)
    (is_sampling_location mountain2 soil)
    (is_sampling_location mountain3 soil)
    
    (traversable base_station mountain1)
    (traversable mountain1 base_station)
    (traversable mountain3 base_station)
    (traversable base_station mountain3)

    (traversable mountain1 mountain2)
    (traversable mountain2 mountain1)
    
    (traversable mountain2 mountain3)
    (traversable mountain3 mountain2)
    
    (operational soil_sampler_1)
    (can_sample_soil soil_sampler_1)
    
    (contaminated base_station soil)
    (contaminated mountain1 soil)
    ; (contaminated mountain2 soil)
    (contaminated mountain3 soil)

    ; start a storm
    ; (is_storm_at base_station)
    ; (not (operational soil_sampler_1))
    ; (storm_occurred)
)

(:goal (and
    ; (sample_collected alex soil mountain2)
    ; (at alex mountain2)
    ; (placed soil_sampler_1 mountain2)
    ; (sample_collected alex soil mountain2 soil_sampler_1)
    ; (landed_space_ship)
    (valid_samples_found soil)
    ; (storm_occurred)
    ; (mission_failed)
))

)

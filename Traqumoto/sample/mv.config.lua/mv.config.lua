local config = {}

function locationFormater (subname, version, sampleName)
    local sampleLocationFormat = "sample/mv.%s.config.lua/%s/mv.%s.config.%s.%s.lua"
    return sampleLocationFormat:format(subname, version, subname, version, sampleName)
end

config.entrainement = dofile(locationFormater("entrainement", "v1-0-0", "sample-0"))
config.environnement = dofile(locationFormater("environnement", "v1-0-0", "sample-0"))

return config
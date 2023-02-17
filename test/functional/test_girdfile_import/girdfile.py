from package import PATH_TARGET, create_target

import gird

gird.rule(
    target=PATH_TARGET,
    recipe=create_target,
)

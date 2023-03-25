from package_test_girdfile_import import PATH_TARGET, create_target

import gird

gird.rule(
    target=PATH_TARGET,
    recipe=create_target,
)

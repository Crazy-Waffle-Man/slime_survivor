from pgone import *

class attack:
    def __init__(self, dmg, cdw, aoe = 0, stun = 1):
        """
        The functionality of attacks.
        Args:
            dmg (int): the amount of damage the attack does.
            cdw (float): How many seconds between uses of the attack?
            pos (tuple): Where is it?
            aoe (int): size of the aoe circle, if 0, it can only hit one enemy
            stun (float, optional): multiplier of the knockback the attack does
        """
        self.damage = dmg
        self.cooldown = cdw
        self.cooldown_remaining = 0
        self.stuntime = stun
        self.area_of_effect = 10 * aoe
        if self.stuntime <= 0:
            raise Exception(f"{self} has invalid stuntime; will lead to error when defining sprites.")
    
    def attack(self, pos, target_pos):
        """
        Args:
            pos (tuple): the (x, y) coordinates of where the attack is.
            target_pos (tuple): the (x, y) of where the target is.
        """
        if self.area_of_effect >= 0:
            if (pos[0] - target_pos[0])**2 + (pos[1] - target_pos[1])**2 <= self.area_of_effect **2:
                return self.damage
            else:
                return 0
        elif self.area_of_effect == 0:
            if pos == target_pos:
                return self.damage
            else:
                return 0
        else:
            print("Negative AOE is not allowed. The sign is negated here so that the program continues running.")
            self.area_of_effect = -self.area_of_effect
            return self.attack(pos, target_pos)
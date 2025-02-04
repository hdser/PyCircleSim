from .balancerv2lbpfactory.create import BalancerV2LBPFactoryCreate

from .balancerv2lbpfactory.disable import BalancerV2LBPFactoryDisable


from .erc20.approve import ERC20Approve

from .erc20.decreaseAllowance import ERC20DecreaseAllowance

from .erc20.transferAndCall import ERC20TransferAndCall

from .erc20.pull import ERC20Pull

from .erc20.decreaseApproval import ERC20DecreaseApproval

from .erc20.claimTokens import ERC20ClaimTokens

from .erc20.transferFrom import ERC20TransferFrom

from .erc20.finishMinting import ERC20FinishMinting

from .erc20.renounceOwnership import ERC20RenounceOwnership

from .erc20.transfer import ERC20Transfer

from .erc20.transferOwnership import ERC20TransferOwnership

from .erc20.burn import ERC20Burn

from .erc20.permit import ERC20Permit

from .erc20.mint import ERC20Mint

from .erc20.increaseAllowance import ERC20IncreaseAllowance

from .erc20.move import ERC20Move

from .erc20.setBridgeContract import ERC20SetBridgeContract

from .erc20.increaseApproval import ERC20IncreaseApproval

from .erc20.push import ERC20Push


from .circleserc20lift.ensureERC20 import CirclesERC20LiftEnsureERC20



from .balancerv2vault.registerPool import BalancerV2VaultRegisterPool

from .balancerv2vault.queryBatchSwap import BalancerV2VaultQueryBatchSwap

from .balancerv2vault.batchSwap import BalancerV2VaultBatchSwap

from .balancerv2vault.setRelayerApproval import BalancerV2VaultSetRelayerApproval

from .balancerv2vault.registerTokens import BalancerV2VaultRegisterTokens

from .balancerv2vault.swap import BalancerV2VaultSwap

from .balancerv2vault.deregisterTokens import BalancerV2VaultDeregisterTokens

from .balancerv2vault.manageUserBalance import BalancerV2VaultManageUserBalance

from .balancerv2vault.setAuthorizer import BalancerV2VaultSetAuthorizer

from .balancerv2vault.setPaused import BalancerV2VaultSetPaused

from .balancerv2vault.managePoolBalance import BalancerV2VaultManagePoolBalance

from .balancerv2vault.flashLoan import BalancerV2VaultFlashLoan

from .balancerv2vault.exitPool import BalancerV2VaultExitPool

from .balancerv2vault.joinPool import BalancerV2VaultJoinPool


from .circleshub.operateFlowMatrix import CirclesHubOperateFlowMatrix

from .circleshub.setAdvancedUsageFlag import CirclesHubSetAdvancedUsageFlag

from .circleshub.registerGroup import CirclesHubRegisterGroup

from .circleshub.safeBatchTransferFrom import CirclesHubSafeBatchTransferFrom

from .circleshub.stop import CirclesHubStop

from .circleshub.groupMint import CirclesHubGroupMint

from .circleshub.safeTransferFrom import CirclesHubSafeTransferFrom

from .circleshub.registerCustomGroup import CirclesHubRegisterCustomGroup

from .circleshub.personalMint import CirclesHubPersonalMint

from .circleshub.registerHuman import CirclesHubRegisterHuman

from .circleshub.trust import CirclesHubTrust

from .circleshub.burn import CirclesHubBurn

from .circleshub.calculateIssuanceWithCheck import CirclesHubCalculateIssuanceWithCheck

from .circleshub.registerOrganization import CirclesHubRegisterOrganization

from .circleshub.wrap import CirclesHubWrap

from .circleshub.setApprovalForAll import CirclesHubSetApprovalForAll

from .circleshub.migrate import CirclesHubMigrate


from ._custom.setupLBP import SetupLBP

from ._custom.joinLBP import JoinLBP


# Implementation registry
IMPLEMENTATIONS = {
    "balancerv2lbpfactory_create": BalancerV2LBPFactoryCreate,
    "balancerv2lbpfactory_disable": BalancerV2LBPFactoryDisable,
    "erc20_approve": ERC20Approve,
    "erc20_decreaseAllowance": ERC20DecreaseAllowance,
    "erc20_transferAndCall": ERC20TransferAndCall,
    "erc20_pull": ERC20Pull,
    "erc20_decreaseApproval": ERC20DecreaseApproval,
    "erc20_claimTokens": ERC20ClaimTokens,
    "erc20_transferFrom": ERC20TransferFrom,
    "erc20_finishMinting": ERC20FinishMinting,
    "erc20_renounceOwnership": ERC20RenounceOwnership,
    "erc20_transfer": ERC20Transfer,
    "erc20_transferOwnership": ERC20TransferOwnership,
    "erc20_burn": ERC20Burn,
    "erc20_permit": ERC20Permit,
    "erc20_mint": ERC20Mint,
    "erc20_increaseAllowance": ERC20IncreaseAllowance,
    "erc20_move": ERC20Move,
    "erc20_setBridgeContract": ERC20SetBridgeContract,
    "erc20_increaseApproval": ERC20IncreaseApproval,
    "erc20_push": ERC20Push,
    "circleserc20lift_ensureERC20": CirclesERC20LiftEnsureERC20,
    "circleserc20lift_ensureERC20_template": CirclesERC20LiftEnsureERC20,
    "balancerv2vault_registerPool": BalancerV2VaultRegisterPool,
    "balancerv2vault_queryBatchSwap": BalancerV2VaultQueryBatchSwap,
    "balancerv2vault_batchSwap": BalancerV2VaultBatchSwap,
    "balancerv2vault_setRelayerApproval": BalancerV2VaultSetRelayerApproval,
    "balancerv2vault_registerTokens": BalancerV2VaultRegisterTokens,
    "balancerv2vault_swap": BalancerV2VaultSwap,
    "balancerv2vault_deregisterTokens": BalancerV2VaultDeregisterTokens,
    "balancerv2vault_manageUserBalance": BalancerV2VaultManageUserBalance,
    "balancerv2vault_setAuthorizer": BalancerV2VaultSetAuthorizer,
    "balancerv2vault_setPaused": BalancerV2VaultSetPaused,
    "balancerv2vault_managePoolBalance": BalancerV2VaultManagePoolBalance,
    "balancerv2vault_flashLoan": BalancerV2VaultFlashLoan,
    "balancerv2vault_exitPool": BalancerV2VaultExitPool,
    "balancerv2vault_joinPool": BalancerV2VaultJoinPool,
    "circleshub_operateFlowMatrix": CirclesHubOperateFlowMatrix,
    "circleshub_setAdvancedUsageFlag": CirclesHubSetAdvancedUsageFlag,
    "circleshub_registerGroup": CirclesHubRegisterGroup,
    "circleshub_safeBatchTransferFrom": CirclesHubSafeBatchTransferFrom,
    "circleshub_stop": CirclesHubStop,
    "circleshub_groupMint": CirclesHubGroupMint,
    "circleshub_safeTransferFrom": CirclesHubSafeTransferFrom,
    "circleshub_registerCustomGroup": CirclesHubRegisterCustomGroup,
    "circleshub_personalMint": CirclesHubPersonalMint,
    "circleshub_registerHuman": CirclesHubRegisterHuman,
    "circleshub_trust": CirclesHubTrust,
    "circleshub_burn": CirclesHubBurn,
    "circleshub_calculateIssuanceWithCheck": CirclesHubCalculateIssuanceWithCheck,
    "circleshub_registerOrganization": CirclesHubRegisterOrganization,
    "circleshub_wrap": CirclesHubWrap,
    "circleshub_setApprovalForAll": CirclesHubSetApprovalForAll,
    "circleshub_migrate": CirclesHubMigrate,
    # Custom implementations
    "custom_setupLBP": SetupLBP,
    "custom_joinLBP": JoinLBP,
}
